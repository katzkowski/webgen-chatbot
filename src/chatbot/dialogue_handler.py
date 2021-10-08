import os
import random
from pathlib import Path
from typing import Any, Callable, Dict, List

from dotenv import load_dotenv
from pandas.core.frame import DataFrame
from spacy.language import Language

from action_handler import ActionHandler
from cluster_selector import ClusterSelector
from context import Context
from hint_provider import HintProvider
from response import Response

load_dotenv()
DATA_PATH = Path(os.getenv("DATA_PATH"))


class DialogueHandler:
    """Handles the dialogue between user and chatbot."""

    def __init__(
        self,
        sid: str,
        nlp: Language,
        answers: Dict[str, Any],
        hints: Dict[str, Any],
        patterns: List[Dict[str, Any]],
        rankings: DataFrame,
        get_ctx_stack: Callable,
    ) -> None:
        self.answers = answers
        self.hint_provider = HintProvider(hints=hints)
        self.action_handler = ActionHandler(
            sid, nlp, patterns=patterns, get_ctx_stack=get_ctx_stack
        )
        self.cluster_selector = ClusterSelector(rankings=rankings)

    def get_answer(self, context: Context) -> str:
        """Return a random answer for a specific intent.

        Args:
            context (Context): conversation context object

        Returns:
            str: answer to be send to user
        """
        try:
            # get list of answers from dict
            answer_list = self.answers[context.intent["name"]][str(context.state)]
        except KeyError:
            return random.choice(self.answers["fallback"]["0"])
        # choose answer randomly from list
        return random.choice(answer_list)

    def get_response(self, context: Context) -> Response:
        """Generate a response to the user for a given context and execute actions if necessary.

        Args:
            context (Context): conversation context object

        Returns:
            Response: response with message, hints, website spec, generate bool
        """
        action_name = context.intent["action"]
        spec = None
        generate = False
        fetch = False

        if action_name:
            try:
                # get function for action name
                action = getattr(self.action_handler, action_name)
            except AttributeError:
                # action function does not exist
                print(f"AttributeError: ActionHandler does not implement {action_name}")

                # show fallback answer and hints
                answer = random.choice(self.answers["fallback"]["0"])
                hints = self.hint_provider.hints["fallback"]["0"]

                return Response(answer, hints, None, generate)
            else:
                # call function specified in intent
                data = action(context)

                # update context state
                intent_state = data["state"]
                context.state = intent_state

                # update generate if in dict
                if "generate" in data:
                    generate = data["generate"]

                    if data["generate"]:
                        # overwrite cluster_id with overall best
                        context.website_spec.data[
                            "cluster_id"
                        ] = self.cluster_selector.get_cluster(
                            context.website_spec, "ALL"
                        )
                        print("overall best: ", context.website_spec.data["cluster_id"])

                # update fetch if in dict
                if "fetch" in data:
                    fetch = data["fetch"]

                # if in create context and no category cluster has been calculated
                if (
                    context.intent["name"] == "create"
                    and "cluster_id" not in context.website_spec.data
                ):
                    # get best-matching cluster for category
                    best_cat_cluster = self.cluster_selector.get_cluster(
                        context.website_spec, "CAT"
                    )

                    if best_cat_cluster is not None:
                        context.website_spec.data["cluster_id"] = best_cat_cluster
                        print(
                            "best category cluster: ",
                            best_cat_cluster,
                        )

        # choose random answer for intent
        answer = self.get_answer(context)

        # get matching hints
        hints = self.hint_provider.get_hints(context)

        # current website_spec
        spec = context.website_spec

        return Response(answer, hints, spec, generate, fetch)
