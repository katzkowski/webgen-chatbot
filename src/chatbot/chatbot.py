from typing import Any, Dict, List, Optional, Union

from pandas.core.frame import DataFrame
from spacy.language import Language

from context import Context
from context_manager import ContextManager
from dialogue_handler import DialogueHandler
from intent_classifier import IntentClassifier
from response import Response


class Chatbot:
    """Represents a chatbot for communication with a single user."""

    def __init__(
        self,
        sid: str,
        nlp: Language,
        intents: List[Dict[str, Any]],
        patterns: List[Dict[str, Union[str, List[Any]]]],
        answers: Dict[str, Dict[str, List[str]]],
        hints: Dict[str, Dict[str, List[str]]],
        rankings: DataFrame = None,
    ) -> None:
        """Initialize a chatbot instance.

        Args:
            sid (str): user session id
            nlp (Language): spaCy language to use
            intents (List[Dict[str, Any]]): intents for classification
            patterns (List[Dict[str, Union[str, List[Any]]]]): list of patterns with joined tokens
            answers (Dict[str, Dict[str, List[str]]]): answers for each intent
            hints (Dict[str, Dict[str, List[str]]]): hints for each intent
        """
        self.ctx_manager = ContextManager(cnx_id=sid)
        self.nlp = nlp
        self.intents = intents
        self.intent_clf = IntentClassifier(nlp, intents=intents)
        self.dialogue_handler = DialogueHandler(
            sid,
            nlp,
            answers=answers,
            hints=hints,
            patterns=patterns,
            rankings=rankings,
            get_ctx_stack=self.ctx_manager.get_stack,
        )
        self.using_generated = True

    def __str__(self) -> str:
        return f"""
            Chatbot instance:
                - Context manager: {str(self.ctx_manager)}
                - Intents: {str(self.intents)}
                - Current website request: {str(self.ctx_manager.current.website_spec)} 
            """

    def process_message(self, msg: str) -> Response:
        """Apply the pipeline, process the message and return an response.

        Args:
            msg (str): user message to the chatbot

        Returns:
            Response: response with message, hints, website spec
        """
        # apply pipeline
        doc = self.nlp(msg.lower())

        current = self.ctx_manager.current

        if (
            current.intent["name"] == "create"
            or current.intent["name"] == "rate"
            or current.intent["name"] == "color"
            or current.intent["name"] == "overlay"
            or current.intent["name"] == "scale"
        ):
            cur_state = current.state

            # push next context with website spec
            ctx = Context(
                current.intent,
                doc,
                cur_state,
                current.website_spec,
            )
            self.ctx_manager.push(ctx)
        elif current.intent["name"] == "ask_next":
            # classify intent
            intent = self.intent_clf.classify(doc)

            # check for intents that need previous context
            if intent["name"] == "alternatives":
                # generate new image with same spec
                ctx = Context(self.intents["create"], doc, 3, current.website_spec)
                # reset color list
                ctx.website_spec.hex = []
                self.ctx_manager.push(ctx)
            elif intent["name"] == "color":
                ctx = Context(intent, doc, 0, current.website_spec)
                # reset color list
                ctx.website_spec.hex = []
                self.ctx_manager.push(ctx)
            elif intent["name"] == "overlay":
                ctx = Context(intent, doc, 0, current.website_spec)

                # reset overlay image
                ctx.website_spec.data.pop(
                    "overlay", None
                )
                ctx.website_spec.data["scale"] = 100
                self.ctx_manager.push(ctx)
            elif intent["name"] == "scale":
                ctx = Context(intent, doc, 0, current.website_spec)
                self.ctx_manager.push(ctx)
            else:
                # reset context stack
                self.ctx_manager.drop_from(1)

                # create new context without website spec
                ctx = Context(intent, doc, 0)
                self.ctx_manager.push(ctx)
        else:
            # classify intent
            intent = self.intent_clf.classify(doc)

            # create new context without website spec
            ctx = Context(intent, doc, 0)
            self.ctx_manager.push(ctx)

        # query response from DialogueHandler
        response = self.dialogue_handler.get_response(ctx)

        return response

    def greet(self) -> Response:
        """Greet user after instance initialization.

        Returns:
            Response: response with message, hints, website spec
        """
        # greet upon init
        greet_ctx = Context(self.intents["greet"], None, 0)
        self.ctx_manager.push(greet_ctx)

        return self.dialogue_handler.get_response(greet_ctx)

    def ask_rating(self) -> Response:
        """Ask the user to rate a generated image.

        Returns:
            Response: response with message, hints, website spec
        """
        current = self.ctx_manager.current

        rating_ctx = Context(self.intents["rate"], None, 0, current.website_spec)
        self.ctx_manager.push(rating_ctx)

        return self.dialogue_handler.get_response(rating_ctx)

    def followup(self) -> Optional[Response]:
        """Push and execute the follow-up intent if defined and if current has reached its final state.

        Returns:
            Optional[Response]: response with message, hints, website spec, or None.
        """
        current = self.ctx_manager.current
        response = None

        # check if final state of intent was reached
        if (
            current.state in current.intent["final"]
            and current.intent["follow-up"] is not None
        ):
            # push new context with follow up intent
            followup_ctx = Context(
                self.intents[current.intent["follow-up"]], None, 0, current.website_spec
            )
            self.ctx_manager.push(followup_ctx)
            response = self.dialogue_handler.get_response(followup_ctx)

        return response
