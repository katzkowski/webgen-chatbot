import re


class Label:
    """Represents a label."""

    def __init__(self, label_name: str, label_type: str, label_href: str) -> None:
        """
        Args:
            label_name (str): name of the label
            label_type (str): type of label, e. g. 'category' or 'color'
            label_href (str): append to url to retrieve all websites with label
        """
        self.name = label_name
        self.label_type = label_type.lower()
        self.href = label_href

    def __str__(self) -> str:
        return f"('{self.name}', type '{self.label_type}', href: '{self.href}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Label):
            return NotImplemented

        return (
            self.name == other.name
            and self.label_type == other.label_type
            and self.href == other.href
        )

    def validate(self):
        """Validates the lable for MySQL database. Label is valid, if no error is raised.

        Raises:
            TypeError:  Invalid label name type
                        Invalid label_type type
            ValueError: Invalid label name length
                        Invalid label_type length
                        Invalid label href length
                        Label href pattern mismatch
        """
        if self.name is None or not isinstance(self.name, str):
            raise TypeError("Invalid label name type.")

        if not len(self.name) <= 255:
            raise ValueError("Invalid label name length.")

        if self.label_type is None or not isinstance(self.name, str):
            raise TypeError("Invalid label_type type.")

        if not len(self.label_type) <= 255:
            raise ValueError("Invalid label_type length")

        if self.href is None or not isinstance(self.href, str):
            raise TypeError("Invalid label href type.")

        if not len(self.href) <= 255:
            raise ValueError("Invalid label href length.")

        if not self.label_type == "country":
            # lowercase, digits, '-', full string match only
            href_pattern = re.compile("^([a-z]+|[0-9]+|[-])+$")

            if not href_pattern.match(self.href):
                raise ValueError("Label href pattern mismatch.")
