import json
import os
import random
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from flask import Flask, request
from flask_socketio import SocketIO
from google.cloud import storage
from unsplash.api import Api
from unsplash.auth import Auth

import pipeline as pipe
from chatbot import Chatbot
from website_spec import WebsiteSpec

load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT")
DATA_PATH = Path(os.getenv("DATA_PATH"))
SECRET_KEY = os.getenv("SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
API_ACCESS_KEY = os.getenv("API_ACCESS_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
API_REDIRECT_URI = os.getenv("API_REDIRECT_URI")

if ENVIRONMENT == "production":
    PORT = int(os.getenv("PORT"))
else:
    PORT = 5000

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

socketio = SocketIO(app, ping_timeout=1000, ping_interval=25)
socketio.init_app(app, cors_allowed_origins="*")

storage_client = None
bucket = None

if ENVIRONMENT == "production":
    # instantiates a client
    storage_client = storage.Client.from_service_account_info(
        json.loads(os.getenv("SERVICE_ACCOUNT"))
    )

    # connect to bucket
    bucket = storage_client.get_bucket(BUCKET_NAME)

# dict for chatbot instances, keys: session id
instances = {}

# queue for incoming user messages: Tuple[request.sid, msg]
msg_handling_queue = []

# Unsplash API
auth = None
api = None


@socketio.on("connect")
def create_chatbot() -> None:
    """Create a new chatbot instance for a new user connection."""
    sid = request.sid
    print(f"Session id {sid}")
    bot = get_bot_instance(sid=sid)

    # greet new user
    response = bot.greet()

    socketio.emit(
        "message",
        response.to_dict(),
        room=sid,
    )


@socketio.on("disconnect")
def delete_chatbot() -> None:
    """Delete chatbot instance after user disconnected."""
    sid = request.sid

    # upload ratings to bucket
    if ENVIRONMENT == "production":
        # get ratings file if exists
        file_name = f"ratings_{sid}.jsonl"
        file_path = DATA_PATH / "ratings" / f"ratings_{sid}.jsonl"

        if file_path.is_file():
            # upload to bucket
            blob = bucket.blob(f"ratings/{file_name}")
            blob.upload_from_filename(filename=str(file_path))
            print(f"Ratings uploaded for client {sid}")

            # remove ratings file from disk
            os.remove(file_path)
        else:
            print("No ratings file to be uploaded")

    instances[sid] = None
    print(f"Client {sid} disconnected")


@socketio.on("message")
def handle_message(data) -> None:
    """Distribute an incoming user message to the correct chatbot instance and send an answer back.

    Args:
        data (Dict[any]): message data
    """
    sid = request.sid
    print(f"Received msg: {data}, Session id {sid}")

    # push to queue
    msg_handling_queue.append((sid, data["message"]))

    while len(msg_handling_queue) != 0:
        qsid, qmsg = msg_handling_queue.pop(0)

        bot = get_bot_instance(sid=qsid)

        # generate answer
        response = bot.process_message(qmsg)

        # send answer and spec
        socketio.emit(
            "message",
            response.to_dict(),
            room=qsid,
        )

        if response.generate:
            # send image
            send_image(qsid, response.website_spec, bot.using_generated)

        if response.fetch and "overlay" in response.website_spec.data:
            # if api image has been requested
            url = get_api_image(response.website_spec.data["overlay"])

            send_overlay(qsid, url)

        if "overlay" not in response.website_spec.data:
            # reset overlay by sending None as url
            send_overlay(qsid, None)

        followup_exists = True

        # get responses of all follow up intents
        while followup_exists:
            response = bot.followup()

            # send followup message if response is not None
            if response:
                socketio.emit(
                    "message",
                    response.to_dict(),
                    room=qsid,
                )
            else:
                # abort loop
                followup_exists = False


@socketio.on("version")
def set_version(data) -> None:
    """Set the image generation mode.

    Args:
        data (Dict[Any]): dict{version: bool}
    """
    sid = request.sid
    bot = get_bot_instance(sid)

    # update bot instance image source
    bot.using_generated = data["version"]
    print(f"Using version: {bot.using_generated}")


def start_server() -> None:
    """Start the server and setup the nlp pipeline."""
    global nlp, intents, patterns, answers, hints, rankings
    nlp, intents, patterns, answers, hints, rankings = pipe.setup_pipeline(bucket)
    print("NLP pipeline setup")

    connect_to_unsplash()
    print("Connected to Unsplash API")

    # start app
    if ENVIRONMENT == "production":
        print(f"Using port {str(PORT)}")
        print("Starting server..")
        socketio.run(app, host="0.0.0.0", port=PORT)
    else:
        # development server
        print("Starting development server..")
        socketio.run(app, debug=True)


def get_bot_instance(sid: str) -> Chatbot:
    """Return an existing bot instance for the session id, or create a new one.

    Args:
        sid (str): session id

    Returns:
        Chatbot: bot instance
    """
    # check if instance exists
    try:
        instance = instances[sid]
    except KeyError:
        print("Creating new instance..")
        # no existing instance found, create new
        instance = Chatbot(
            sid,
            nlp=nlp,
            intents=intents,
            patterns=patterns,
            answers=answers,
            hints=hints,
            rankings=rankings,
        )
        instances[sid] = instance
    return instance


def send_image(sid: str, website_spec: WebsiteSpec, use_generated: bool = True) -> None:
    """Get an image based on a website specification and send it to the user identified by `sid`.

    Args:
        sid (str): the user session id
        website_spec (WebsiteSpec): website specification object
        use_generated (bool): use generated images. Defaults to True.
    """
    # get image as bytes
    if use_generated:
        image_bytes = get_generated_image(
            cluster_id=website_spec.data["cluster_id"], use_bucket=True
        )
    else:
        image_bytes = get_training_image(
            cluster_id=website_spec.data["cluster_id"], use_bucket=True
        )

    socketio.emit("image", {"image": image_bytes}, room=sid)


def send_overlay(sid: str, url: str) -> None:
    """Sends an url to an overlay image to a client.

    Args:
        sid (str): session id
        url (str): url to image
    """
    socketio.emit(
        "overlay",
        {"url": url},
        room=sid,
    )


def get_generated_image(cluster_id: int, use_bucket: bool) -> Optional[bytes]:
    """Returns a generated image from the specified cluster.

    Args:
        cluster_id (int): id of source cluster
        use_bucket (bool): if True use gcloud bucket, else file system

    Returns:
        Optional[bytes]: image as byte representation, or None.
    """
    if use_bucket and bucket is not None:
        # target cluster
        target_cluster_path = (
            f"generated/transfer_m70_v02_k55_c{cluster_id}-generated-71"
        )

        print(f"Using cluster {cluster_id}")

        # choose random image from cluster folder
        image_no = random.choice(list(range(0, 100)))
        print("Selected image no ", image_no)

        # construct path for bucket
        image_path = f"{target_cluster_path}/generated-{image_no}-ema.jpg"

        # get blob from bucket
        blob = bucket.get_blob(image_path)

        # return image as binary, or None
        if blob:
            blob_bytes = blob.download_as_bytes()
            return blob_bytes

        print("image blob is none")
        # else: blob is None
        return blob
    else:
        # target cluster
        target_cluster_path = (
            DATA_PATH
            / "generated"
            / (f"transfer_m70_v02_k55_c{cluster_id}-generated-71")
        )

        print(f"Using cluster {cluster_id}")

        # choose random image from cluster folder
        image_path = target_cluster_path / random.choice(
            [
                image
                for image in os.listdir(target_cluster_path)
                if os.path.isfile(os.path.join(target_cluster_path, image))
            ]
        )

        # return image as binary
        with open(image_path, "rb") as f:
            image = f.read()
        return image


def get_training_image(cluster_id: int, use_bucket: bool) -> Optional[bytes]:
    """Returns a training image from the specified cluster.

    Args:
        cluster_id (int): id of source cluster
        use_bucket (bool): if True use gcloud bucket, else file system (not implemented)

    Returns:
        Optional[bytes]: image as byte representation, or None.
    """
    if use_bucket:
        # target cluster
        target_cluster_path = f"datasets/v02_k55_c{cluster_id}"
        print(f"Using cluster {cluster_id}")

        # get list of image blobs in target cluster
        blobs = storage_client.list_blobs(BUCKET_NAME, prefix=target_cluster_path)

        # choose random image blob from cluster folder
        blob = random.choice([b for b in blobs])
        print("Selected image blob: ", blob)

        # return selected image as binary, or None
        if blob:
            blob_bytes = blob.download_as_bytes()
            return blob_bytes

        print("image blob is none")
        # else: blob is None
        return blob
    else:
        raise NotImplementedError


def connect_to_unsplash() -> None:
    """Connects the server to the Unsplash API."""
    global auth, api

    client_id = API_ACCESS_KEY
    client_secret = API_SECRET_KEY
    redirect_uri = API_REDIRECT_URI
    auth = Auth(client_id, client_secret, redirect_uri)
    api = Api(auth)


def get_api_image(keyword: str) -> Optional[Dict[str, str]]:
    """Returns a random image matching the keyword from the Unsplash API.

    Args:
        keyword (str): keyword for image search

    Returns:
        Optional[Dict[str,str]]: {img_url, user, username}, or None.
    """
    if keyword is not None:
        data = api.search.photos(keyword)
        try:
            photo = random.choice(data["results"])
            link = photo.urls.thumb
            user = photo.user.name
            username = photo.user.username
            return {"link": link, "user": user, "username": username}
        except Exception:
            pass
    return None


# app start
start_server()
