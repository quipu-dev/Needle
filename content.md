## [WIP] feat: 实现 pyneedle-bus 核心组件 (EventBus, FeedbackBus, MessageStore)

### 用户需求

填充 `pyneedle-bus` 的核心代码。
1.  **升级 `pyneedle-spec`**：定义通用的 `GenericEventIR` 数据结构和 `RendererProtocol` 协议。
2.  **更新依赖**：让 `pyneedle-bus` 依赖 `pyneedle-runtime` 以复用 Operator 体系。
3.  **实现 `MessageStore`**：作为 Operator 的编排者，管理多资源根并构建 OverlayOperator，不再手动加载 JSON。
4.  **实现 `EventBus`**：支持 `SemanticPointer` 订阅的逻辑总线。
5.  **实现 `FeedbackBus`**：基于 `MessageStore` 和 `Renderer` 的表达层总线。
6.  **实现 `LogBridge`**：连接 Event 和 Feedback 的桥梁。

### 评论

这是一个非常清晰且架构合理的重构。将 `MessageStore` 转型为 "Operator Orchestrator" 是点睛之笔，它完美利用了 `pyneedle-runtime` 已有的能力，避免了代码重复（DRY原则），并且天然支持了分层覆盖（Overlay）和懒加载（Lazy Loading）。

### 目标

1.  在 `pyneedle-spec` 中定义 `GenericEventIR` 和 `RendererProtocol`。
2.  更新 `pyneedle-bus/pyproject.toml` 添加 `pyneedle-runtime`。
3.  实现 `pyneedle-bus` 的所有核心 Python 模块。

### 基本原理

1.  **Spec First**: 只有先定义好了数据结构（`GenericEventIR`）和接口（`RendererProtocol`），Bus 的实现才有依据。
2.  **Reuse Runtime**: `pyneedle-runtime` 提供了强大的文件系统和字典操作符，`MessageStore` 只需要负责将它们组合起来（Compose），而不需要重新实现文件读取逻辑。
3.  **Semantic Pointer everywhere**: 无论是 Event 的 Topic 还是 Feedback 的 Template Key，都统一使用 `SemanticPointer` (L) 作为一等公民。

### 标签

#intent/build #flow/ready #priority/high #comp/bus #comp/spec #concept/event #concept/i18n #scope/core #task/domain/bus #task/object/core-implementation #task/action/implementation #task/state/continue

---

### Script

#### Acts 1: 升级 `pyneedle-spec` (GenericEventIR & RendererProtocol)

首先，我们需要在规范层定义通用的事件结构和渲染器协议。

~~~~~act
write_file
packages/pyneedle-spec/src/needle/spec/events.py
~~~~~
~~~~~python
from typing import TypedDict, Dict, Any, Optional

class GenericEventIR(TypedDict):
    """
    The universal envelope for events in the PyNeedle ecosystem.
    
    This structure is designed to be:
    1. Serializable (JSON-safe)
    2. Minimalist (Only essential headers)
    3. Extensible (Via tags and payload)
    """
    v: str              # Protocol version (e.g. "1.0")
    ts: float           # Unix timestamp
    topic: str          # The routing key (often stringified SemanticPointer)
    
    # Metadata for routing, filtering, and tracing.
    # e.g. {"env": "prod", "source": "worker-1", "level": "error"}
    tags: Dict[str, str] 
    
    # The actual business data.
    # For Cascade, this contains 'ctx' and 'phy' data.
    payload: Dict[str, Any]
~~~~~

~~~~~act
patch_file
packages/pyneedle-spec/src/needle/spec/protocols.py
~~~~~
~~~~~python
class OperatorProtocol(Protocol):
    def __call__(self, key: Any) -> Any: ...
~~~~~
~~~~~python
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
    RendererProtocol,
)
from .events import GenericEventIR

__all__ = [
    "SemanticPointerProtocol",
    "PointerSetProtocol",
    "OperatorProtocol",
    "RendererProtocol",
    "GenericEventIR",
]
~~~~~

#### Acts 2: 更新 `pyneedle-bus` 依赖

为了使用 `I18NFactoryOperator` 等工具，bus 必须依赖 runtime。

~~~~~act
patch_file
packages/pyneedle-bus/pyproject.toml
~~~~~
~~~~~toml
dependencies = [
    "pyneedle-spec ~= 0.1.0",
    "pyneedle-pointer ~= 0.1.0",
]
~~~~~
~~~~~toml
dependencies = [
    "pyneedle-spec ~= 0.1.0",
    "pyneedle-pointer ~= 0.1.0",
    "pyneedle-runtime ~= 0.1.0",
]
~~~~~

#### Acts 3: 实现 `EventBus` (The Nervous System)

这是一个纯逻辑的消息分发器，支持 `SemanticPointer` 订阅。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/event.py
~~~~~
~~~~~python
import time
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type, Union, Optional

from needle.spec import GenericEventIR, SemanticPointerProtocol

# Type alias for event handlers
# Handlers receive the raw event object (or Dict if published as dict)
EventHandler = Callable[[Any], None]


class EventBus:
    """
    A high-performance, in-memory event bus supporting Semantic Pointer routing.
    """

    def __init__(self):
        # Mapping: Topic String -> List of Handlers
        self._subscribers: Dict[str, List[EventHandler]] = defaultdict(list)
        # Mapping: Event Type (Class) -> List of Handlers
        self._type_subscribers: Dict[Type[Any], List[EventHandler]] = defaultdict(list)
        # Wildcard or special pattern subscribers could be added here
        
    def subscribe(
        self, 
        topic: Union[str, SemanticPointerProtocol, Type[Any]], 
        handler: EventHandler
    ) -> None:
        """
        Subscribe to events.
        
        Args:
            topic: Can be:
                   - A Semantic Pointer (L.run.started) -> converted to string "run.started"
                   - A string ("run.started")
                   - A Class (RunStartedEvent) -> for type-based dispatch
            handler: Function to call when event occurs.
        """
        if isinstance(topic, type):
            self._type_subscribers[topic].append(handler)
        else:
            # Normalize pointer/string to string key
            key = str(topic)
            self._subscribers[key].append(handler)

    def publish(self, event: Any, topic: Union[str, SemanticPointerProtocol, None] = None) -> None:
        """
        Dispatch an event to subscribers.
        
        Args:
            event: The event object (dataclass, dict, etc.)
            topic: Optional override for the topic. 
                   If event has a 'topic' attribute or key, that is used by default.
                   If event is a SemanticPointer, it is treated as a signal (topic=event, data={}).
        """
        # 1. Determine the topic string
        resolved_topic: str = ""
        
        if topic:
            resolved_topic = str(topic)
        elif hasattr(event, "topic"):
            resolved_topic = str(event.topic)
        elif isinstance(event, dict) and "topic" in event:
            resolved_topic = str(event["topic"])
        elif hasattr(event, "__str__") and not hasattr(event, "__dict__"): 
             # Edge case: publishing a bare SemanticPointer as a signal
             resolved_topic = str(event)
        
        # 2. Dispatch by Topic (String matching)
        if resolved_topic:
            handlers = self._subscribers.get(resolved_topic)
            if handlers:
                for handler in handlers:
                    handler(event)

        # 3. Dispatch by Type (Class matching)
        # This allows Cascade-style typed events: bus.publish(RunStarted(...))
        event_type = type(event)
        type_handlers = self._type_subscribers.get(event_type)
        if type_handlers:
            for handler in type_handlers:
                handler(event)
                
        # Future: Add wildcard matching (e.g. "run.*") if needed.
~~~~~

#### Acts 4: 实现 `MessageStore` (The Orchestrator)

利用 `pyneedle-runtime` 的 Operator 体系，实现零 IO 代码的资源管理。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/store.py
~~~~~
~~~~~python
import os
from pathlib import Path
from typing import List, Dict, Optional

from needle.runtime import I18NFactoryOperator, OverlayOperator
from needle.spec import OperatorProtocol


class MessageStore:
    """
    Orchestrates resource loading using the PyNeedle Operator system.
    
    Instead of manually loading JSONs, it maintains a list of 'Asset Roots'.
    When an operator is requested for a language, it builds an OverlayOperator
    that stacks I18NFactoryOperators for each root.
    """

    def __init__(self):
        # List of paths where 'needle/<lang>/*.json' structures can be found.
        # Order matters: later roots override earlier ones (if we prepend) 
        # or earlier ones override later (if we prepend). 
        # Strategy: New roots are added to the FRONT of the list (High Priority).
        self._asset_roots: List[Path] = []
        
        # Cache operators by language code
        self._operator_cache: Dict[str, OperatorProtocol] = {}

    def register_asset_root(self, path: Path) -> None:
        """
        Register a new directory containing 'needle' assets.
        This directory should contain the 'needle' folder directly? 
        No, usually it points TO the 'needle' folder or the parent?
        
        Convention: The path passed here MUST be the parent of the 'needle' directory.
        e.g. .../src/stitcher/assets  (which contains ./needle/en/...)
        """
        resolved = path.resolve()
        if resolved not in self._asset_roots:
            # Insert at beginning to give higher priority to user/plugin overrides
            self._asset_roots.insert(0, resolved)
            # Invalidate cache because the overlay structure has changed
            self._operator_cache.clear()

    def get_operator(self, lang: str) -> OperatorProtocol:
        """
        Get the fully composed Operator for a specific language.
        """
        if lang in self._operator_cache:
            return self._operator_cache[lang]

        # Build the chain
        operators: List[OperatorProtocol] = []
        for root in self._asset_roots:
            # I18NFactoryOperator takes the 'assets root' and 
            # internally appends "needle/<lang>" when called with a lang pointer.
            # But wait, I18NFactoryOperator(root)(lang_ptr) returns a FileSystemOperator.
            
            factory = I18NFactoryOperator(root)
            # We treat the lang string as a pointer path (e.g. "en")
            # The factory resolves this to root/needle/en
            op = factory(lang)
            operators.append(op)

        # Create the overlay
        # Operators are in priority order (Head of list = Highest Priority)
        overlay = OverlayOperator(operators)
        
        self._operator_cache[lang] = overlay
        return overlay

    @staticmethod
    def detect_lang() -> str:
        """
        Helper to detect system language.
        """
        # 1. Explicit override
        env_lang = os.getenv("NEEDLE_LANG") or os.getenv("STITCHER_LANG")
        if env_lang:
            return env_lang

        # 2. System LANG
        sys_lang = os.getenv("LANG")
        if sys_lang:
            base_lang = sys_lang.split(".")[0].split("_")[0]
            if base_lang:
                return base_lang

        return "en"
~~~~~

#### Acts 5: 实现 `FeedbackBus` (The Expression System)

这是面向用户的接口，负责“查找模板 -> 格式化 -> 渲染”。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/feedback.py
~~~~~
~~~~~python
from typing import Any, Optional, Union

from needle.spec import SemanticPointerProtocol, RendererProtocol
from .store import MessageStore


class FeedbackBus:
    """
    The output channel for the application. Handles I18n lookup and rendering.
    """

    def __init__(self, store: MessageStore, renderer: Optional[RendererProtocol] = None):
        self._store = store
        self._renderer = renderer
        
    def set_renderer(self, renderer: RendererProtocol) -> None:
        self._renderer = renderer

    def _get_template(self, ptr: Union[str, SemanticPointerProtocol]) -> str:
        # 1. Detect Language
        lang = self._store.detect_lang()
        
        # 2. Get Operator for that language
        op = self._store.get_operator(lang)
        
        # 3. Lookup
        template = op(ptr)
        
        # 4. Fallback: If not found, stringify the pointer itself
        if template is None:
            return str(ptr)
            
        return str(template)

    def present(
        self, 
        ptr: Union[str, SemanticPointerProtocol], 
        level: str = "info", 
        **kwargs: Any
    ) -> None:
        """
        Present a message to the user.
        
        Args:
            ptr: Semantic Pointer to the message template (e.g. L.io.file_saved)
            level: 'info', 'success', 'warning', 'error', 'debug'
            **kwargs: Arguments for template formatting
        """
        if not self._renderer:
            return

        template = self._get_template(ptr)
        
        try:
            message = template.format(**kwargs)
        except KeyError as e:
            message = f"<formatting error for '{ptr}': missing key {e}>"
        except Exception as e:
            message = f"<rendering error for '{ptr}': {e}>"

        self._renderer.render(message, level=level, **kwargs)

    # Convenience shortcuts
    
    def info(self, ptr: Union[str, SemanticPointerProtocol], **kwargs: Any) -> None:
        self.present(ptr, level="info", **kwargs)

    def success(self, ptr: Union[str, SemanticPointerProtocol], **kwargs: Any) -> None:
        self.present(ptr, level="success", **kwargs)

    def warning(self, ptr: Union[str, SemanticPointerProtocol], **kwargs: Any) -> None:
        self.present(ptr, level="warning", **kwargs)

    def error(self, ptr: Union[str, SemanticPointerProtocol], **kwargs: Any) -> None:
        self.present(ptr, level="error", **kwargs)
        
    def debug(self, ptr: Union[str, SemanticPointerProtocol], **kwargs: Any) -> None:
        self.present(ptr, level="debug", **kwargs)
~~~~~

#### Acts 6: 实现 `LogBridge` (The Bridge)

实现零配置日志的关键组件。

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
    Connects the EventBus (Logic) to the FeedbackBus (Presentation).
    
    It listens for events and attempts to render them using the FeedbackBus.
    This enables 'Zero-Config Logging' if the Event Topic matches an I18n Key.
    """

    def __init__(self, event_bus: EventBus, feedback_bus: FeedbackBus):
        self.event_bus = event_bus
        self.feedback_bus = feedback_bus

    def connect(
        self, 
        topic: Union[str, SemanticPointerProtocol, Type[Any]], 
        ptr: Union[str, SemanticPointerProtocol, None] = None,
        level: str = "info"
    ) -> None:
        """
        Explicitly map an Event Topic to a Feedback Pointer.
        
        Args:
            topic: The event topic to listen for.
            ptr: The I18n pointer to use for rendering. 
                 If None, assumes topic IS the pointer (Auto-Bridge).
            level: The log level.
        """
        target_ptr = ptr or topic
        
        def handler(event: Any):
            # Extract data for template formatting
            data = {}
            if isinstance(event, dict):
                data = event
            elif hasattr(event, "__dict__"):
                data = event.__dict__
            
            # If the event payload is nested (like Cascade GenericEventIR), 
            # we might want to flatten it or pass specific parts.
            # For now, we pass the whole object structure and let format() access attributes.
            # e.g. "{payload.task_id}"
            
            self.feedback_bus.present(target_ptr, level=level, **data)
            
        self.event_bus.subscribe(topic, handler)
~~~~~

#### Acts 7: 暴露 API

最后，我们在 `__init__.py` 中暴露这些组件，并创建一个默认的单例实例，方便简单应用直接使用。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/__init__.py
~~~~~
~~~~~python
from .event import EventBus, EventHandler
from .feedback import FeedbackBus
from .store import MessageStore
from .bridge import LogBridge

__all__ = [
    "EventBus",
    "EventHandler",
    "FeedbackBus",
    "MessageStore",
    "LogBridge",
    "bus",  # The default FeedbackBus singleton
    "event_bus", # The default EventBus singleton
    "message_store", # The default Store
]

# --- Default Singleton Instances ---
# For simple apps (like CLI tools), a global singleton is often sufficient.
# Complex apps (like Cascade Engine) may instantiate their own buses.

message_store = MessageStore()

# Note: Renderer is not set by default. 
# The application entry point (CLI/Main) must call `bus.set_renderer(...)`
bus = FeedbackBus(store=message_store) 

event_bus = EventBus()
~~~~~

### 下一步建议

`pyneedle-bus` 的核心已经就绪。接下来的步骤是开始“边缘绞杀”：
1.  首先针对 `Stitcher`，移除其 `stitcher-bus`，改为依赖 `pyneedle-bus`。
2.  在 `stitcher` 的入口处配置 `message_store`，注册其 assets 目录。
3.  验证 `stitcher check` 等命令的输出是否正常。
