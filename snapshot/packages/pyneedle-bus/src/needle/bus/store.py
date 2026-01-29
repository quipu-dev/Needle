import json
import logging
from pathlib import Path
from typing import Dict, List, Union

logger = logging.getLogger(__name__)


class MessageStore:
    """
    A multi-root, locale-aware store for message templates.
    """

    def __init__(self, default_locale: str = "en"):
        self._roots: List[Path] = []
        self._messages: Dict[str, str] = {}
        self.locale = default_locale

    def set_locale(self, locale: str) -> None:
        """Sets the active locale and reloads messages."""
        if self.locale != locale:
            self.locale = locale
            self._load_messages()

    def register_asset_root(self, path: Union[str, Path]) -> None:
        """
        Registers a root directory containing a 'locales' subdirectory.
        This allows multiple packages to contribute translations.
        """
        root_path = Path(path)
        if root_path not in self._roots:
            self._roots.append(root_path)
            self._load_messages()

    def _load_messages(self) -> None:
        """Loads and merges all messages from all registered roots for the current locale."""
        self._messages.clear()
        logger.debug(f"Loading messages for locale '{self.locale}' from roots: {self._roots}")

        for root in self._roots:
            locale_path = root / "locales" / self.locale
            if not locale_path.is_dir():
                continue

            for message_file in locale_path.glob("*.json"):
                try:
                    with open(message_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self._messages.update(data)
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Failed to load message file {message_file}: {e}")

        logger.debug(f"Loaded {len(self._messages)} messages for locale '{self.locale}'.")

    def get(self, msg_id: str, default: str = "") -> str:
        """Gets a message template by its ID."""
        return self._messages.get(msg_id, default or f"<{msg_id}>")