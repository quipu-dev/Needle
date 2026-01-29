import logging
from typing import Any, Optional, Union, Callable
from needle.pointer import SemanticPointer
from needle.spec.protocols import Renderer
from .store import MessageStore

logger = logging.getLogger(__name__)


class FeedbackBus:
    """
    Handles the translation of semantic pointers into human-readable messages.
    """

    def __init__(self, operator: Callable[[Union[str, SemanticPointer]], str], store: MessageStore):
        self._renderer: Optional[Renderer] = None
        self._operator = operator
        self._store = store

    def set_renderer(self, renderer: Renderer) -> None:
        """Injects the output renderer (e.g., a console printer)."""
        self._renderer = renderer

    def present(self, msg_id: Union[str, SemanticPointer], level: str = "info", **kwargs: Any) -> None:
        """The core rendering method."""
        if not self._renderer:
            logger.warning(f"FeedbackBus renderer not set. Dropping message: '{msg_id}'")
            return

        # Use the operator to resolve the pointer to a message ID string
        message_key = self._operator(msg_id)
        if message_key is None:
            message_key = str(msg_id)

        template = self._store.get(message_key)
        try:
            message = template.format(**kwargs)
        except KeyError as e:
            fallback_template = self._store.get("sys.error.formatting")
            message = fallback_template.format(msg_id=message_key, key=e)
            logger.warning(message)

        self._renderer.render(message, level)

    def info(self, msg_id: Union[str, SemanticPointer], **kwargs: Any) -> None:
        self.present(msg_id, "info", **kwargs)

    def success(self, msg_id: Union[str, SemanticPointer], **kwargs: Any) -> None:
        self.present(msg_id, "success", **kwargs)

    def warning(self, msg_id: Union[str, SemanticPointer], **kwargs: Any) -> None:
        self.present(msg_id, "warning", **kwargs)

    def error(self, msg_id: Union[str, SemanticPointer], **kwargs: Any) -> None:
        self.present(msg_id, "error", **kwargs)

    def debug(self, msg_id: Union[str, SemanticPointer], **kwargs: Any) -> None:
        self.present(msg_id, "debug", **kwargs)