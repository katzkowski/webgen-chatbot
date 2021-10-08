from typing import Any, Dict, List, Optional

from spacy.tokens import Doc
from website_spec import WebsiteSpec


class Context:
    "Representing a snapshot of the 'memory' of the chatbot"

    def __init__(
        self,
        intent: Dict[str, List[Any]],
        doc: Doc,
        state: int,
        website_spec: Optional[WebsiteSpec] = None,
    ) -> None:
        """Initialize a context.

        Args:
            intent (Dict[str, List[Any]]): intent object
            doc (Doc): user message as spaCy doc
            state (int): state of the intent
            website_spec (Optional[WebsiteSpec], optional): website spec. Defaults to None.
        """
        self.intent = intent
        self.doc = doc
        self.state = state
        if website_spec is None:
            self.website_spec = WebsiteSpec()
        else:
            self.website_spec = website_spec

    def __str__(self) -> str:
        return f"(intent: {self.intent}, doc: {self.doc}, state: {self.state}, website spec: {str(self.website_spec)} )"
