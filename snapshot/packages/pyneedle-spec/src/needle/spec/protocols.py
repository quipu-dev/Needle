from typing import Protocol, Any, Union, Iterable, TypeVar

# T_co is covariant, meaning SemanticPointerProtocol can return subtypes of itself
T_Pointer = TypeVar("T_Pointer", bound="SemanticPointerProtocol", covariant=True)


class SemanticPointerProtocol(Protocol[T_Pointer]):
    def __getattr__(self, name: str) -> T_Pointer: ...

    def __str__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __eq__(self, other: Any) -> bool: ...

    def __add__(self, other: Any) -> T_Pointer: ...

    def __truediv__(
        self, other: Union[str, "SemanticPointerProtocol"]
    ) -> T_Pointer: ...

    def __mul__(self, other: Any) -> "PointerSetProtocol": ...


class PointerSetProtocol(Protocol):
    def __iter__(self) -> Iterable[SemanticPointerProtocol]: ...

    def __truediv__(
        self, other: Union[str, SemanticPointerProtocol]
    ) -> "PointerSetProtocol": ...

    def __or__(self, other: "PointerSetProtocol") -> "PointerSetProtocol": ...

    def __add__(
        self, other: Union[str, SemanticPointerProtocol]
    ) -> "PointerSetProtocol": ...

    def __mul__(self, other: Any) -> "PointerSetProtocol": ...


class OperatorProtocol(Protocol):
    def __call__(self, key: Any) -> Any: ...


class RendererProtocol(Protocol):
    """
    Protocol for feedback rendering systems (CLI, TUI, Web, etc.).
    """

    def render(self, message: str, level: str = "info", **kwargs: Any) -> None:
        """
        Render a pre-formatted message to the user.

        Args:
            message: The fully formatted string (templates resolved).
            level: The severity/channel (info, success, warning, error, debug).
            **kwargs: Extra context for specific renderers (e.g. TUI widgets).
        """
        ...
