import os
from pathlib import Path
from needle.pointer import L
from needle.operators import I18NFactoryOperator, OverlayOperator

from .event import EventBus
from .feedback import FeedbackBus
from .store import MessageStore

# --- 1. Create Core Singletons ---
message_store = MessageStore()
event_bus = EventBus()

# --- 2. Configure the FeedbackBus Operator Pipeline ---
# The default assets are located relative to this file in pyneedle-bus
_default_bus_assets_root = Path(__file__).parent / "assets"

# Register the default root first. User/plugin roots will be layered on top.
message_store.register_asset_root(_default_bus_assets_root)

# This operator factory is configured to ONLY look in our registered store.
# We create a simple callable that uses the singleton store.
def needle_operator(key):
    # 1. Resolve pointer to string key
    # (The default I18N operator would do this, but we simplify for the default bus)
    # In a real scenario, this would be more complex, but for now, str(key) is fine.
    str_key = str(key)
    # 2. Get template from the central store
    return message_store.get(str_key)

# --- 3. Instantiate the FeedbackBus Singleton ---
bus = FeedbackBus(operator=needle_operator, store=message_store)

# --- 4. Dynamic Language Detection ---
def _detect_lang() -> str:
    needle_lang = os.getenv("NEEDLE_LANG")
    if needle_lang:
        return needle_lang
    sys_lang = os.getenv("LANG")
    if sys_lang:
        return sys_lang.split(".")[0].split("_")[0]
    return "en"

# Set initial locale
message_store.set_locale(_detect_lang())