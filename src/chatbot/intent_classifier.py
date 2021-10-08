from typing import Any, Dict

from spacy.language import Language
from spacy.tokens import Doc


class IntentClassifier:
    """Represents an intent classifier instance for user messages."""

    def __init__(self, nlp: Language, intents: Dict[str, Dict[str, Any]]) -> None:
        """Initialize an instance by setting the language and the intents.

        Args:
            nlp (Language): spaCy language to use
            intents (Dict[str, Dict[str, Any]]): intents to use

        """
        self.nlp = nlp
        self.intents = intents

    def classify(self, doc: Doc) -> Dict[str, Any]:
        """Classify the intent of the user message.

        Args:
            doc (Doc): spaCy doc object of the user message

        Returns:
            Dict[str, Any]: the best matching intent
        """
        best_intent = self.intents["fallback"]
        best_match = ("fallback", None, 0)

        # for all tokens, find best matching overall intent
        for token in doc:
            for intent in self.intents.values():
                # compute similarities
                sim = [
                    token.similarity(self.nlp(keyword))
                    for keyword in intent["keywords"]
                ]

                # store new best intent if above threshold
                if sim and max(sim) > 0.6 and max(sim) > best_match[2]:
                    best_intent = intent
                    best_match = (intent, token, max(sim))

                    # if intent has been matched
                    if best_match[2] == 1.0:
                        print(best_match)
                        return best_intent

        print(best_match)
        return best_intent
