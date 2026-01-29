from typing import Protocol, runtime_checkable


@runtime_checkable
class RendererProtocol(Protocol):
    """
    Protocol for components capable of rendering feedback to the user.
    """
    def render(self, message: str, level: str) -> None:
        """
        Render a message with a specific severity level.
        
        Args:
            message: The formatted message string.
            level: The severity level (e.g., 'info', 'success', 'warning', 'error').
        """
        ...