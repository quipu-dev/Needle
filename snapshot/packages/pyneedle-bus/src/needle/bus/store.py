import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MessageStore:
    """
    A centralized registry for loading and retrieving I18n messages from multiple sources.
    
    It supports 'Multi-root Loading', allowing downstream libraries (Stitcher, Quipu)
    to register their own asset directories.
    """

    def __init__(self, locale: str = "en"):
        self._roots: List[Path] = []
        self._messages: Dict[str, str] = {}
        self.locale = locale
        self._loaded = False

    def register_asset_root(self, path: Path) -> None:
        """
        Register a new directory containing locale assets.
        
        Args:
            path: A directory path expected to contain subdirectories for locales
                  (e.g., path/en/messages.json).
        """
        if path not in self._roots:
            self._roots.append(path)
            # If we have already loaded, we need to reload to include new assets
            if self._loaded:
                self.reload()

    def reload(self) -> None:
        """
        Clear cache and reload messages from all registered roots.
        """
        self._messages.clear()
        self._load_messages()

    def _load_messages(self) -> None:
        """
        Internal method to iterate over roots and load JSON files.
        Later roots override earlier ones (Overlay behavior).
        """
        for root in self._roots:
            locale_path = root / self.locale
            if not locale_path.is_dir():
                continue

            for message_file in locale_path.glob("*.json"):
                try:
                    with open(message_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            self._messages.update(data)
                except (json.JSONDecodeError, OSError) as e:
                    logger.error(f"Failed to load message file {message_file}: {e}")
        
        self._loaded = True

    def get(self, msg_id: str, default: str = "") -> str:
        """
        Retrieve a message template by its ID.
        """
        if not self._loaded:
            self._load_messages()
            
        return self._messages.get(msg_id, default or f"<{msg_id}>")