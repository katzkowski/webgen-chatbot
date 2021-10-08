from typing import Any, Dict, List, Tuple


class WebsiteSpec:
    """Represents a website specification with categories, features and additional data."""

    def __init__(
        self,
        cats: List[Tuple[str, str, str]] = None,
        feats: List[Tuple[str, str, str]] = None,
        hex: List[Tuple[str, str, str]] = None,
        data: Dict[Any, Any] = None,
    ) -> None:
        """Initialize a website specification object.

        Args:
            cats (List[Tuple[str, str, str]]): list of categories in pattern format. Defaults to None.
            feats (List[Tuple[str, str, str]]): list of features in pattern format. Defaults to None.
            hex (List[Tuple[str, str, str]]): list of hex colors in pattern format. Defaults to None.
            data (Dict[Any, Any]): dict to hold any data
        """
        self.cats = cats if cats else []
        self.feats = feats if feats else []
        self.hex = hex if hex else []
        self.data = data if data else {}

    def __str__(self) -> str:
        return f"""Website Spec:
        - categories: {self.cats}
        - feats: {self.feats}
        - hex: {self.hex}
        - data: {self.data}"""
