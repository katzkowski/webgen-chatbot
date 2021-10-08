import os
import random
from pathlib import Path
from typing import Dict, List, Union

from dotenv import load_dotenv
from context import Context

load_dotenv()
DATA_PATH = Path(os.getenv("DATA_PATH"))


class HintProvider:
    """Provides the hints for the chatbot."""

    def __init__(
        self, hints: Dict[str, Union[List[str], Dict[str, List[str]]]] = None
    ) -> None:
        """Init a hint_provider instance.

        Args:
            hints (Dict[str, Union[List[str], Dict[str, List[str]]]], optional): Dict of hints, structured as in `hints.json`. Defaults to None.
        """
        self.hints = hints

    def get_hints(self, context: Context, amount: int = 3) -> List[str]:
        """Returns a list of hints to be displayed for a specific intent.

        Args:
            context (Context): conversation context object
            amount (int, optional): amount of hints. Defaults to 3.

        Returns:
            List[str]: list of hints
        """
        if context.intent["name"] == "create" and context.state < 2:
            # use specific hints for create context
            try:
                # use best features for selected cluster as hints
                cluster_id = context.website_spec.data["cluster_id"]
                hints = self.hints["features"][str(cluster_id)]
                print(f"Providing hints for cluster: {cluster_id}")
            except KeyError:
                # use categories instead
                hints = self.hints["categories"]
            return random.sample(hints, k=amount)
        else:
            try:
                # get list of hints from dict
                hints = self.hints[context.intent["name"]][str(context.state)]
            except KeyError:
                # do not show any hints
                return []
            return hints
