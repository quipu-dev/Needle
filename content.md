## [WIP] feat: 填充 pyneedle-bus 核心组件与 spec 定义

### 用户需求

根据架构设计，需要在 `pyneedle-spec` 中定义通用的事件数据结构和协议，并在 `pyneedle-bus` 中实现核心的事件总线、反馈总线和消息存储机制。文档和注释必须使用英文。

### 评论

这是实施路线图的关键执行阶段。我们将 Cascade 的高性能逻辑与 Stitcher 的语义指针灵活性结合。首先在 Spec 层定义“契约”（GenericEventIR），然后在 Bus 层实现“机制”。特别是 `MessageStore` 的多根加载机制，是支持插件化生态的关键。

### 目标

1.  **扩展 Spec**: 在 `pyneedle-spec` 中定义 `GenericEventIR`、`EventProtocol` 和 `RendererProtocol`。
2.  **实现 Store**: 创建 `MessageStore`，支持注册多个资源根目录（Asset Roots）以加载 I18n 消息。
3.  **实现 FeedbackBus**: 移植 Stitcher 的逻辑，使其依赖新的 `MessageStore` 和 `RendererProtocol`。
4.  **实现 EventBus**: 移植 Cascade 的逻辑并增强，使其支持基于 `SemanticPointer` 的主题订阅和分发。
5.  **实现 Bridge**: 提供将 Event 自动转换为 Feedback 的 `LogBridge` 骨架。

### 基本原理

1.  **GenericEventIR**: 定义为 `TypedDict` 以确保运行时开销最小化，同时保持结构清晰。
2.  **EventBus**: 采用混合路由策略。保留 Cascade 的基于类型的订阅（用于强类型逻辑），同时增加基于字符串 Topic（支持 L 指针）的订阅。
3.  **MessageStore**: 不再硬编码路径，而是维护一个 `Path` 列表，加载时按注册顺序合并字典，实现“覆盖”机制。
4.  **英文文档**: 严格遵守代码库规范，确保国际化友好。

### 标签

#intent/build #flow/ready #priority/high #comp/bus #comp/spec #concept/event #concept/i18n #scope/core #task/domain/bus #task/object/core-implementation #task/action/implementation #task/state/continue

---

### Script

#### Acts 1: 扩展 pyneedle-spec 定义

首先，我们在规范层定义通用的事件结构和渲染协议。

~~~~~act
write_file
packages/pyneedle-spec/src/needle/spec/events.py
~~~~~
~~~~~python
from typing import TypedDict, Dict, Any, Protocol, runtime_checkable


class GenericEventIR(TypedDict):
    """
    The universal envelope for events in the PyNeedle ecosystem.
    
    This structure allows disparate systems (Cascade, Stitcher, Quipu) to share
    a common event bus without sharing implementation details.
    """
    v: str              # Protocol version (e.g. "1.0")
    ts: float           # Unix timestamp
    topic: str          # The routing key (e.g. "needle.core.started")
    tags: Dict[str, str]  # Lightweight metadata for routing/filtering
    payload: Dict[str, Any] # The actual event data


@runtime_checkable
class EventProtocol(Protocol):
    """
    Protocol that any Event object must satisfy to be transmissible via the bus.
    """
    @property
    def topic(self) -> str:
        """Return the routing topic for this event."""
        ...

    def to_ir(self) -> GenericEventIR:
        """Serialize the event to the generic intermediate representation."""
        ...
~~~~~

~~~~~act
write_file
packages/pyneedle-spec/src/needle/spec/presentation.py
~~~~~
~~~~~python
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
~~~~~

~~~~~act
patch_file
packages/pyneedle-spec/src/needle/spec/__init__.py
~~~~~
~~~~~python
from .protocols import (
    SemanticPointerProtocol,
    PointerSetProtocol,
    OperatorProtocol,
)

__all__ = [
    "SemanticPointerProtocol",
    "PointerSetProtocol",
    "OperatorProtocol",
]
~~~~~
~~~~~python
from .protocols import (
    SemanticPointerProtocol,
    PointerSetProtocol,
    OperatorProtocol,
)
from .events import GenericEventIR, EventProtocol
from .presentation import RendererProtocol

__all__ = [
    "SemanticPointerProtocol",
    "PointerSetProtocol",
    "OperatorProtocol",
    "GenericEventIR",
    "EventProtocol",
    "RendererProtocol",
]
~~~~~

#### Acts 2: 实现 MessageStore (资源层)

实现支持多根加载的消息存储。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/store.py
~~~~~
~~~~~python
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
~~~~~

#### Acts 3: 实现 FeedbackBus (表达层)

移植 FeedbackBus，连接 Store 和 Renderer。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/feedback.py
~~~~~
~~~~~python
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
~~~~~

#### Acts 4: 实现 EventBus (逻辑层)

移植并增强 EventBus，支持 L 指针订阅。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/event.py
~~~~~
~~~~~python
import asyncio
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type, Union

from needle.spec import EventProtocol, SemanticPointerProtocol

# Handler type alias
Handler = Callable[[Any], None]


class EventBus:
    """
    The Nervous System of PyNeedle.
    
    A high-performance, in-memory event bus supporting both 
    Type-based subscription (for logic) and Topic-based subscription (for routing).
    """

    def __init__(self):
        # Type-based subscribers: EventClass -> [handlers]
        self._type_subscribers: Dict[Type[Any], List[Handler]] = defaultdict(list)
        
        # Topic-based subscribers: "topic.string" -> [handlers]
        self._topic_subscribers: Dict[str, List[Handler]] = defaultdict(list)
        
        # Wildcard topic subscribers: "topic.*" -> [handlers]
        # Currently we support simple prefix matching logic or just global wildcard.
        # For simplicity in V1, we handle "*" specially.
        self._wildcard_subscribers: List[Handler] = []

    def subscribe(
        self, 
        target: Union[str, SemanticPointerProtocol, Type[Any]], 
        handler: Handler
    ):
        """
        Subscribe a handler to an event type or topic.
        
        Args:
            target: Can be a Python class (Type), a string topic, or a SemanticPointer.
            handler: The function to call when the event occurs.
        """
        if isinstance(target, str):
            if target == "*":
                self._wildcard_subscribers.append(handler)
            else:
                self._topic_subscribers[target].append(handler)
        elif hasattr(target, "__str__") and not isinstance(target, type):
            # SemanticPointer or similar object
            self._topic_subscribers[str(target)].append(handler)
        else:
            # Assume it's a type (Class)
            self._type_subscribers[target].append(handler)

    def publish(self, event: Any):
        """
        Publish an event to all interested subscribers.
        
        Dispatch Logic:
        1. Exact Type match
        2. Exact Topic match (if event has .topic)
        3. Wildcards
        """
        # 1. Dispatch by Type
        event_type = type(event)
        if event_type in self._type_subscribers:
            for handler in self._type_subscribers[event_type]:
                self._safe_call(handler, event)

        # 2. Dispatch by Topic
        topic = getattr(event, "topic", None)
        # If it's a SemanticPointer, convert to string
        if hasattr(topic, "__str__"):
            topic = str(topic)
            
        if topic and isinstance(topic, str):
            if topic in self._topic_subscribers:
                for handler in self._topic_subscribers[topic]:
                    self._safe_call(handler, event)

        # 3. Wildcards
        for handler in self._wildcard_subscribers:
            self._safe_call(handler, event)

    def _safe_call(self, handler: Handler, event: Any):
        """Execute handler, suppressing exceptions to prevent bus crash."""
        try:
            handler(event)
        except Exception as e:
            # In a real scenario, we might want to log this via a fallback mechanism
            # or emit a SystemError event (careful of infinite loops).
            # For now, we print to stderr as a last resort.
            import sys
            print(f"[EventBus] Error in handler {handler}: {e}", file=sys.stderr)
~~~~~

#### Acts 5: 实现 Bridge (胶水层)

实现 `LogBridge`，自动将事件转换为反馈。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/bridge.py
~~~~~
~~~~~python
from typing import Any, Type, Union
from needle.spec import SemanticPointerProtocol

from .event import EventBus
from .feedback import FeedbackBus


class LogBridge:
    """
    The Synapse connecting the EventBus (Nervous System) to the FeedbackBus (Expression System).
    
    It listens for events and automatically renders them as user feedback 
    if a corresponding message template exists.
    """

    def __init__(self, event_bus: EventBus, feedback_bus: FeedbackBus):
        self.event_bus = event_bus
        self.feedback_bus = feedback_bus

    def connect(
        self, 
        event_type: Union[Type[Any], str, SemanticPointerProtocol], 
        ptr: SemanticPointerProtocol, 
        level: str = "info"
    ):
        """
        Establish a connection: When `event_type` occurs, render `ptr` template.
        
        Args:
            event_type: The event to listen for (Class or Topic/Pointer).
            ptr: The Semantic Pointer pointing to the I18n message key.
            level: The log level to use.
        """
        def handler(event: Any):
            # Extract data from event. 
            # We support both object attributes (via __dict__) and dictionary access.
            if isinstance(event, dict):
                data = event
            elif hasattr(event, "__dict__"):
                data = event.__dict__
            else:
                data = {}
            
            self.feedback_bus.info(ptr, **data) if level == "info" else \
            self.feedback_bus.success(ptr, **data) if level == "success" else \
            self.feedback_bus.warning(ptr, **data) if level == "warning" else \
            self.feedback_bus.error(ptr, **data) if level == "error" else \
            self.feedback_bus.debug(ptr, **data)

        self.event_bus.subscribe(event_type, handler)
~~~~~

#### Acts 6: 导出包内容

最后，更新 `__init__.py` 导出这些新组件。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/__init__.py
~~~~~
~~~~~python
from .event import EventBus
from .feedback import FeedbackBus
from .store import MessageStore
from .bridge import LogBridge

__all__ = ["EventBus", "FeedbackBus", "MessageStore", "LogBridge"]
~~~~~

### 下一步建议

`pyneedle-bus` 的核心已经就绪。现在我们需要验证它的功能，然后开始对 Stitcher 进行“心脏移植”。建议创建一个简单的测试用例，模拟 Event -> Bus -> Bridge -> Feedback -> Renderer 的完整链路，确保各组件协同工作正常。
