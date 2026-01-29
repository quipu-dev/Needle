from typing import Any, Optional, Union
from needle.spec import RendererProtocol, SemanticPointerProtocol
from .store import MessageStore


class FeedbackBus:
    """
    The Expression System of PyNeedle.
    
    Responsible for converting abstract semantic pointers into human-readable 
    feedback using the MessageStore and a Renderer.
    """

    def __init__(self, store: MessageStore):
        self._store = store
        self._renderer: Optional[RendererProtocol] = None

    def set_renderer(self, renderer: RendererProtocol) -> None:
        """Attach a physical renderer (e.g., TUI, Console, Web)."""
        self._renderer = renderer

    def _render(
        self, level: str, msg_id: Union[str, SemanticPointerProtocol], **kwargs: Any
    ) -> None:
        if not self._renderer:
            return

        key = str(msg_id)
        template = self._store.get(key)

        try:
            message = template.format(**kwargs)
        except KeyError as e:
            message = f"<formatting_error for '{key}': missing key {e}>"

        self._renderer.render(message, level)

    def info(self, msg_id: Union[str, SemanticPointerProtocol], **kwargs: Any) -> None:
        self._render("info", msg_id, **kwargs)

    def success(self, msg_id: Union[str, SemanticPointerProtocol], **kwargs: Any) -> None:
        self._render("success", msg_id, **kwargs)

    def warning(self, msg_id: Union[str, SemanticPointerProtocol], **kwargs: Any) -> None:
        self._render("warning", msg_id, **kwargs)

    def error(self, msg_id: Union[str, SemanticPointerProtocol], **kwargs: Any) -> None:
        self._render("error", msg_id, **kwargs)

    def debug(self, msg_id: Union[str, SemanticPointerProtocol], **kwargs: Any) -> None:
        self._render("debug", msg_id, **kwargs)

    def render_to_string(
        self, msg_id: Union[str, SemanticPointerProtocol], **kwargs: Any
    ) -> str:
        """
        Helper to just get the formatted string without sending to renderer.
        """
        key = str(msg_id)
        template = self._store.get(key)
        try:
            return template.format(**kwargs)
        except KeyError:
            return f"<formatting_error for '{key}'>"