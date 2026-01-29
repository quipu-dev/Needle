好的，骨架已经就绪。现在我们开始为这个新的神经中枢注入生命。我们将按照分析的路线图，分步实现 `EventBus`、`FeedbackBus`、`MessageStore` 及其连接件。

这是一个宏大的重构计划，我将一步到位，生成所有核心组件的初始实现。

## [WIP] feat(bus): 实现 EventBus, FeedbackBus 和 MessageStore

### 用户需求

根据架构统一计划，需要为新创建的 `pyneedle-bus` 包填充核心实现。这包括：
1.  从 `Cascade` 移植并泛化 `EventBus`，使其支持 `SemanticPointer`。
2.  从 `Stitcher` 移植 `FeedbackBus` 的渲染和操作符逻辑。
3.  从 `Cascade` 和 `Quipu` 移植 `MessageStore`，并增加多资源根的注册能力。
4.  定义 `Renderer` 协议并将其放入 `pyneedle-spec`。
5.  创建一个工厂来实例化并导出全局单例 `bus` 和 `event_bus`。

### 评论

这是统一大业的核心执行阶段。我们正在将三个独立项目中经过实战检验的最佳实践（Cascade 的事件分发、Stitcher 的语义化反馈、Quipu 的多通道输出理念）融合到一个单一、健壮的包中。这一步完成后，`pyneedle-bus` 将成为一个功能完备的“超集”，为后续的“绞杀”阶段提供强大的武器。特别是 `MessageStore` 的多资源根加载机制，是实现插件化架构和生态系统扩展性的关键。

### 目标

1.  在 `pyneedle-spec` 中建立标准的 `Renderer` 协议。
2.  在 `pyneedle-bus` 中提供一个功能完整的 `EventBus`，能够按类型和语义主题进行订阅/发布。
3.  提供一个功能完整的 `FeedbackBus`，由可注入的操作符驱动，能够进行 I18n 渲染。
4.  提供一个可扩展的 `MessageStore`，能够从多个包中发现并加载 `locales` 资源。
5.  通过 `needle.bus` 命名空间暴露易于使用的 `bus` 和 `event_bus` 单例。
6.  为 `pyneedle-bus` 添加对 `pyneedle-runtime` 的依赖，以使用其中的操作符。

### 基本原理

我们将采用模块化的方式，逐个文件创建和实现核心组件。
1.  首先，修改 `pyneedle-spec` 和 `pyneedle-bus` 的 `pyproject.toml`，奠定协议和依赖基础。
2.  然后，创建 `store.py`、`feedback.py` 和 `event.py`，分别从现有代码库中移植、清理和泛化核心逻辑。
3.  接着，创建 `factory.py`，这是整个系统的“启动程序”，它负责将所有组件装配在一起，并配置 I18n 管道。
4.  最后，通过 `__init__.py` 文件定义清晰的公共 API，向上层应用屏蔽实现细节。
这种自底向上的构建方式确保了各组件职责清晰，依赖关系正确。

### 标签

#intent/build #flow/ready #priority/high #comp/bus #concept/event-sourcing #concept/i18n #scope/core #ai/instruct #task/domain/bus #task/object/core-implementation #task/action/implementation #task/state/continue

---

### Script

#### Acts 1: 奠定协议与依赖基础

首先，我们在 `pyneedle-spec` 中定义 `Renderer` 协议，并为 `pyneedle-bus` 添加对 `pyneedle-runtime` 的依赖，以便使用操作符。

~~~~~act
patch_file
packages/pyneedle-spec/src/needle/spec/protocols.py
~~~~~
~~~~~python.old
class OperatorProtocol(Protocol):
    def __call__(self, key: Any) -> Any: ...
~~~~~
~~~~~python.new
class OperatorProtocol(Protocol):
    def __call__(self, key: Any) -> Any: ...


class Renderer(Protocol):
    """
    The protocol for rendering feedback messages to an output stream (like a console).
    """

    def render(self, message: str, level: str) -> None:
        """
        Renders a message with a specified severity level.

        Args:
            message: The final, formatted string to be displayed.
            level: A string representing the severity (e.g., "info", "error").
        """
        ...
~~~~~

~~~~~act
patch_file
packages/pyneedle-bus/pyproject.toml
~~~~~
~~~~~toml
dependencies = [
    "pyneedle-spec ~= 0.1.0",
    "pyneedle-pointer ~= 0.1.0",
]
classifiers = [
~~~~~
~~~~~toml
dependencies = [
    "pyneedle-spec ~= 0.1.0",
    "pyneedle-pointer ~= 0.1.0",
    "pyneedle-runtime ~= 0.1.0",
]
classifiers = [
~~~~~

~~~~~act
patch_file
packages/pyneedle-bus/pyproject.toml
~~~~~
~~~~~toml
[tool.uv.sources]
pyneedle-spec = { workspace = true }
pyneedle-pointer = { workspace = true }
~~~~~
~~~~~toml
[tool.uv.sources]
pyneedle-spec = { workspace = true }
pyneedle-pointer = { workspace = true }
pyneedle-runtime = { workspace = true }
~~~~~

#### Acts 2: 创建资源文件和 `MessageStore`

我们创建 `MessageStore`，它是 `FeedbackBus` 的 i18n 引擎，并为其提供一些默认的系统消息。

~~~~~act
run_command
~~~~~
~~~~~
mkdir -p packages/pyneedle-bus/src/needle/bus/assets/locales/en
~~~~~

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/assets/locales/en/sys.json
~~~~~
~~~~~json
{
    "sys.error.fallback": "An unexpected system error occurred.",
    "sys.error.formatting": "<Formatting error for '{msg_id}': missing key {key}>"
}
~~~~~

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/store.py
~~~~~
~~~~~python
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
~~~~~

#### Acts 3: 实现 `EventBus`

移植自 `Cascade`，这是系统的逻辑神经中枢。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/event.py
~~~~~
~~~~~python
from collections import defaultdict
from typing import Callable, List, Type, Dict, Any, Union
from needle.pointer import SemanticPointer

Handler = Callable[[Any], None]


class EventBus:
    """
    A high-performance, in-memory bus for system event distribution.
    Supports subscribing by event type, semantic pointer, or string topic.
    """

    def __init__(self):
        # Type-based subscriptions: {EventType: [handler1, handler2]}
        self._type_subscribers: Dict[Type, List[Handler]] = defaultdict(list)
        # Topic-based subscriptions: {"topic.string": [handler1, handler2]}
        self._topic_subscribers: Dict[str, List[Handler]] = defaultdict(list)
        # Wildcard subscribers that receive all events
        self._wildcard_subscribers: List[Handler] = []

    def subscribe(self, topic: Union[Type, str, SemanticPointer], handler: Handler) -> None:
        """Subscribes a handler to a specific event type or topic."""
        if isinstance(topic, type):
            self._type_subscribers[topic].append(handler)
        elif isinstance(topic, (str, SemanticPointer)):
            self._topic_subscribers[str(topic)].append(handler)
        else:
            # A special case for a global wildcard subscription
            self._wildcard_subscribers.append(handler)

    def publish(self, event: Any, topic: Union[str, SemanticPointer, None] = None) -> None:
        """Publishes an event object or a topic with data to all relevant subscribers."""
        # 1. Notify type-based subscribers
        event_type = type(event)
        if event_type in self._type_subscribers:
            for handler in self._type_subscribers[event_type]:
                handler(event)

        # 2. Determine topic and notify topic-based subscribers
        final_topic = topic or getattr(event, "topic", None)
        if final_topic:
            topic_str = str(final_topic)
            if topic_str in self._topic_subscribers:
                for handler in self._topic_subscribers[topic_str]:
                    # For topic-based events, the event object itself is passed
                    handler(event)
        
        # TODO: Implement glob/wildcard matching for topics.

        # 3. Notify global wildcard subscribers
        for handler in self._wildcard_subscribers:
            handler(event)
~~~~~

#### Acts 4: 实现 `FeedbackBus`

移植自 `Stitcher`，这是系统的用户表达系统。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/feedback.py
~~~~~
~~~~~python
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
~~~~~

#### Acts 5: 创建工厂并导出单例

这是将所有组件连接在一起并提供易用接口的关键。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/factory.py
~~~~~
~~~~~python
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
~~~~~

#### Acts 6: 定义公共 API

最后，我们通过 `__init__.py` 暴露公共接口。

~~~~~act
patch_file
packages/pyneedle-bus/src/needle/bus/__init__.py
~~~~~
~~~~~python.old
# pyneedle-bus: Unified EventBus (logic) and FeedbackBus (presentation)
~~~~~
~~~~~python.new
# pyneedle-bus: Unified EventBus (logic) and FeedbackBus (presentation)

from .factory import bus, event_bus, message_store
from .event import EventBus
from .feedback import FeedbackBus
from .store import MessageStore

__all__ = ["bus", "event_bus", "message_store", "EventBus", "FeedbackBus", "MessageStore"]
~~~~~

### 下一步建议

`pyneedle-bus` 的核心功能现已就绪。
1.  **实现 Bridge**: 接下来，我们可以创建 `bridge.py`，实现 `EventToFeedbackBridge`，以完成逻辑层和表达层的自动连接。
2.  **开始绞杀**: 我们已经具备了替换 `stitcher-bus` 的所有条件。下一个计划可以是对 Stitcher 进行“心脏移植手术”，将其完全切换到 `pyneedle-bus`。这将是对新架构的第一次实战检验。
