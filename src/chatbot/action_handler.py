import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from spacy.language import Language
from spacy.tokens import Doc

from context import Context

load_dotenv()
DATA_PATH = Path(os.getenv("DATA_PATH"))
ENVIRONMENT = os.getenv("ENVIRONMENT")


class ActionHandler:
    "Executes actions specified in intents."

    def __init__(
        self,
        sid: str,
        nlp: Language,
        patterns: List[Dict[str, Any]],
        get_ctx_stack: Callable,
    ) -> None:
        """Initialize an ActionHandler instance.

        Args:
            nlp (Language): spaCy language
            patterns (List[Dict[str, Any]]): patterns for spaCy EntityRuler
            get_ctx_stack (Callable): returns the current context stack
        """
        self.sid = sid
        self.nlp = nlp
        self.patterns = patterns
        self.get_ctx_stack = get_ctx_stack

    def extract_website_spec(self, context: Context) -> Dict[str, Any]:
        """Handle website specification process, which consists of 3 steps, and then return a specification dict for the website.

        1. Ask website category
        2. Ask website features
        3. Ask website color

        Args:
            context (Context): current context

        Returns:
            Dict[str, Any]: {"state": int, Optional["generate": bool]}
        """
        # get categories if empty
        if not context.website_spec.cats:
            cats = self.get_entities(context.doc, "CAT")
            if cats:
                context.website_spec.cats = cats
                print("Setting cats: ", cats)
            else:
                return {"state": 0}

        # get features if empty
        if not context.website_spec.feats:
            feats = self.get_entities(context.doc, "FEAT")
            if feats:
                context.website_spec.feats = feats
                print("Setting feats: ", feats)
            else:
                return {"state": 1}

        return {"state": 2, "generate": True}

    def handle_rating(self, context: Context) -> Dict[str, Any]:
        """Handle website rating process, consisting of two steps.

        1. Ask for rating
        2. Store rating

        Args:
            context (Context): current context

        Returns:
            Dict[str, Any]: {"state": int, Optional["generate": bool]}
        """
        if context.state == 0:
            # user is being asked, no action required
            return {"state": 1}
        else:
            # get cardinal entities
            cardinal_ents = [
                ent.text for ent in context.doc.ents if ent.label_ == "CARDINAL"
            ]
            print(f"cardinal_ents: {cardinal_ents}")

            if cardinal_ents:
                # use first cardinal entitiy
                rating = int(cardinal_ents[0])

                if rating not in range(0, 6):
                    print("Invalid rating given")
                    # return invalid rating status, ask again
                    return {"state": 0}
                else:
                    print(f"Rating : {str(rating)}")
            else:
                print("Invalid rating given")
                # return invalid rating status, ask again
                return {"state": 0}

            rating_dict = {}

            # user rating
            rating_dict["rating"] = rating

            # get doc strings from context stack
            ctx_stack = self.get_ctx_stack()
            rating_dict["inputs"] = [
                ctx.doc.text for ctx in ctx_stack if ctx.intent["name"] == "create"
            ]

            # website spec as dict
            rating_dict["website_spec"] = context.website_spec.__dict__

            # store in ratings.json
            self.store_rating(rating_dict)

            return {"state": int(2 + rating)}

    def handle_color_change(self, context: Context) -> Dict[str, Any]:
        """Determine to which color the website shall be changed and update the context.

        Args:
            context (Context): current context

        Returns:
            Dict[str, Any]: {"state": int, Optional["generate": bool]}
        """
        if not context.website_spec.hex:
            hex = self.get_entities(context.doc, "HEX")
            if hex:
                context.website_spec.hex = hex
                return {"state": 1}
            else:
                return {"state": 0}
        else:
            return {"state": 1}

    def handle_reset(self, context: Context) -> Dict[str, Any]:
        """Resets overlay image and color.

        Args:
            context (Context): current context

        Returns:
            Dict[str, Any]: "state": int}
        """
        context.website_spec.hex = []
        context.website_spec.data.pop("overlay", None)
        context.website_spec.data["scale"] = 100
        return {"state": 0}

    def handle_overlay(self, context: Context) -> Dict[str, Any]:
        """Extract keywords for overlay image.

        Args:
            context (Context): current context

        Returns:
            Dict[str, Any]: {"state": int, Optional["fetch": bool]}
        """
        try:
            if not context.website_spec.data["overlay"]:
                overlay_content = str(context.doc)
                print(overlay_content)
                if overlay_content:
                    context.website_spec.data["overlay"] = overlay_content
                    return {"state": 1, "fetch": True}
                else:
                    return {"state": 0}
            else:
                return {"state": 1}
        except KeyError:
            context.website_spec.data["overlay"] = None
            return {"state": 0}

    def handle_scale(self, context: Context) -> Dict[str, Any]:
        """Set scale for overlay image.

        Args:
            context (Context): current context

        Returns:
            Dict[str, Any]: {"state": int}
        """
        # check if an overlay image was added
        try:
            if not context.website_spec.data["overlay"]:
                return {"state": 3}
        except KeyError:
            return {"state": 3}

        # check if scale is specified in website_spec
        if context.doc is None or "scale" not in context.website_spec.data:
            return {"state": 0}

        # get cardinal entities for width scaling
        cardinal_ents = [
            ent.text for ent in context.doc.ents if ent.label_ == "CARDINAL"
        ]
        print(f"cardinal_ents: {cardinal_ents}")

        if cardinal_ents:
            # use first cardinal entitiy
            scale = int(cardinal_ents[0])

            if scale not in range(25, 201):
                print("Invalid scale given")
                # return invalid scale, ask again
                return {"state": 2}
            else:
                context.website_spec.data["scale"] = scale
                print(f"Scale : {str(scale)}")
                return {"state": 1}
        else:
            print("Invalid scale given")
            # return invalid scale status, ask again
            return {"state": 2}

    def store_rating(self, rating: Dict[str, Any]) -> None:
        """Store dict with rating data in `ratings.jsonl`.

        Args:
            rating (Dict[str, Any]): ratings data
        """
        if ENVIRONMENT == "production":
            # temp rating file for sid
            ratings_json = DATA_PATH / "ratings" / (f"ratings_{self.sid}.jsonl")
        else:
            ratings_json = DATA_PATH / "chatbot" / "ratings.jsonl"

        # append rating to temp file for sid
        with open(ratings_json, "a+") as json_file:
            json.dump(rating, json_file)
            json_file.write("\n")

    def sim_entity(self, doc: Doc, entity_type: str) -> Optional[str]:
        """Returns the best matching entity regarding similarity score.

        Args:
            doc (Doc): spaCy doc object of the user message
            entity_type (str): type of desired entity

        Returns:
            Tuple[float, Tuple[str, str, str]]: best entity matching with similarity score and entity tuple
        """
        # only patterns with specified entity type (label)
        ents = [
            (pat["pattern"].lower(), pat["label"], pat["id"])
            for pat in self.patterns
            if pat["label"] == entity_type
        ]

        sim = []
        # compute similarities
        for token in doc:
            print(f"Token '{token}' entity type: {token.ent_type_}")
            # if token is already part of an entity, skip it
            if token.ent_type_ != "HEX" and token.ent_type_ != "":
                continue

            # token similarity with each entity pattern
            t_sim = [(token.similarity(self.nlp(ent[0])), ent) for ent in ents]
            sim = [*sim, *t_sim]

        # if sim list is empty
        if not sim:
            return None

        # return ent with highest score
        best_ent = max(sim, key=lambda tpl: tpl[0])
        print(best_ent)

        if best_ent[0] > 0.7:
            return best_ent[1]
        else:
            return None

    def get_entities(self, doc: Doc, entity_type: str) -> List[Tuple[str, str, str]]:
        """Get entities from the doc of a specific `entity_type` using pattern and word similarity, if there is no pattern match.

        Args:
            doc (Doc): spaCy doc object of the user message
            entity_type (str): "CAT", "FEAT" or "HEX"

        Returns:
            List[Tuple[str, str, str]]: list of entity tuples
        """
        # get entites of entity_type
        ents = [
            (ent.text, ent.label_, ent.ent_id_)
            for ent in doc.ents
            if ent.label_ == entity_type
        ]

        # if no entity found, use similarity entity matcher and best match
        if not ents:
            best_ent = self.sim_entity(doc, entity_type)
            return [best_ent] if best_ent is not None else []
        else:
            return ents
