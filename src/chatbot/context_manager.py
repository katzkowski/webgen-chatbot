from typing import List, Union

from context import Context


class ContextManager:
    "Manages context for a chatbot instance."

    def __init__(self, cnx_id: str) -> None:
        """Initialize a context manager for a specific user connection.

        Args:
            cnx_id (str): id of the user connection to the server
        """
        self.cnx_id = cnx_id
        self.stack = []
        self.current_idx = -1
        self.current = None

    def __str__(self) -> str:
        name = f"""Context manager for connection {self.cnx_id}
        - Current context index: {self.current_idx}
        - Current stack:"""

        # print each context in stack
        stack = list(
            map(
                lambda ctx: str(ctx.intent["name"]) + ", state: " + str(ctx.state),
                self.stack,
            )
        )

        # print stack items with indentation
        return "\n           ".join([name] + stack)

    def get_stack(self) -> List[Context]:
        """Returns the current context stack.

        Returns:
            List[Context]: current context stack as new list object
        """
        return [] + self.stack

    def push(self, ctx: Context) -> None:
        """Push a new context to the context stack.

        Args:
            ctx (Context): the new context
        """
        self.stack.append(ctx)
        self.current_idx += 1
        self.current = self.stack[self.current_idx]
        print(self)

    def pop(self) -> Context:
        """Pop a context from the context stack and return it. The context (at the stack's base is never removed.

        Returns:
            Context: context on top of stack
        """
        #  never pop first context
        if len(self.stack) > 1:
            self.current_idx -= 1
            self.current = self.stack[self.current_idx]
            return self.stack.pop()
        else:
            return self.stack[0]

    def previous(self) -> Context:
        """Set the current context to the previous context on the stack and return it.

        Returns:
            Context: the new current context
        """
        # set context to previous in context stack
        if self.current_idx > 0:
            self.current_idx -= 1
            self.current = self.stack[self.current_idx]

        return self.stack[self.current_idx]

    def drop_from(self, position: Union[int, str] = "previous") -> None:
        """Drop all contexts starting from a certain position on the stack.

        Args:
            position (Union[int, str], optional):
                If int: drop context starting at index.
                If str, position to drop from can either be "previous" or "current".
                Defaults to "previous".

        Raises:
            ValueError: if position is int and position < 1
                        if position is str and not in ["previous", "current"]
        """
        if isinstance(position, int):
            if position >= 1:
                self.stack = self.stack[:position]
                self.current_idx = position - 1
                self.current = self.stack[self.current_idx]
                print(f"Stack after drop {list(map(str, self.stack))}")
                return
            else:
                raise ValueError(f"Cannot drop from position < 1")

        # isinstance(position, str)
        if position == "previous":
            self.previous()
            self.stack = self.stack[: (self.current_idx + 1)]
        elif position == "current":
            self.stack = self.stack[: (self.current_idx + 1)]
        else:
            raise ValueError(f"Unknown position option {position} in drop_from.")
