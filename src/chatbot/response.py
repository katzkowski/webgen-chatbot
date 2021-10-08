from typing import Any, Dict, List, Optional

from website_spec import WebsiteSpec


class Response:
    """Represents a response object that holds data to process and send to the client.

    Object attributes:
        message (str): message to send to user
        hints (List[str]): list of hints
        website_spec (Optional[WebsiteSpec], optional): Optional website specification object. Defaults to None.
        generate (bool): True if a website shall be generated. Defaults to False.
        fetch (bool): True if an overlay image shall be fetched. Defaults to False.
    """

    def __init__(
        self,
        message: str,
        hints: List[str],
        website_spec: Optional[WebsiteSpec] = None,
        generate: bool = False,
        fetch: bool = False,
    ) -> None:
        """Initialize a Response object.

        Args:
            message (str): message to send to user
            hints (List[str]): list of hints
            website_spec (Optional[WebsiteSpec], optional): Optional website specification object. Defaults to None.
            generate (bool): True if a website shall be generated. Defaults to False.
            fetch (bool): True if an overlay image shall be fetched. Defaults to False.
        """
        self.message = message
        self.hints = hints
        self.website_spec = website_spec
        self.generate = generate
        self.fetch = fetch

    def __str__(self) -> str:
        return str(
            {
                "message": self.message,
                "hints": self.hints,
                "website_spec": self.website_spec,
                "generate": self.generate,
                "fetch": self.fetch,
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "hints": self.hints,
            "spec": self.website_spec.__dict__,
            "generate": self.generate,
            "fetch": self.fetch,
        }
