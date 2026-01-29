分析完全正确。目前的 `MessageStore` 实际上是一个“伪装成存储的配置组装器”，它把“如何检测语言”、“如何定位文件”以及“如何构建 Overlay”这些**业务策略**硬编码进了 `pyneedle-bus` 这个本应纯粹的**通信基础设施**中。

这违反了“关注点分离”原则：
1.  **Bus** 应该只关心：我有消息（Pointer），我有渲染器（Renderer），我需要一个黑盒（Operator）帮我把消息转换成模板。
2.  **Runtime** 应该提供构建这个黑盒的零件（I18NFactory, Overlay）。
3.  **Application (Stitcher)** 应该决定如何组装这些零件。

我将执行第一步：净化 `pyneedle-bus`。

## [WIP] refactor(bus): 从 FeedbackBus 中解构并删除 MessageStore

### 用户需求
移除 `pyneedle-bus` 中对 `MessageStore` 的硬编码依赖。使 `FeedbackBus` 成为一个纯粹的、接受 `OperatorProtocol` 注入的展示总线，从而实现“策略（如何加载资源）”与“机制（如何分发和渲染消息）”的彻底解耦。

### 评论
这是迈向“本体论正确性”的关键一步。通过将 `FeedbackBus` 泛化为仅依赖 `OperatorProtocol` 的组件，我们不仅消除了 Bus 对文件系统的隐式依赖，还极大地增强了系统的灵活性——现在我们可以轻易地注入一个基于内存、数据库甚至远程 API 的 Operator，而无需修改总线代码。

### 目标
1.  **删除** `packages/pyneedle-bus/src/needle/bus/store.py`。
2.  **重构** `FeedbackBus`：
    *   移除 `MessageStore` 依赖。
    *   增加 `set_operator` 方法用于延迟注入。
    *   简化模板获取逻辑，直接通过 `self._operator(ptr)` 获取。
3.  **更新** `pyneedle-bus` 入口：
    *   不再导出 `MessageStore` 或 `message_store`。
    *   初始化一个空的 `bus` 单例。

### 基本原理
根据 **HFEA v1.0** 的“严格分层与边界”公理，Bus 属于“执行（Action）”层，而 Operator 的组装属于“意图（Intent）”层。通过依赖倒置（Dependency Inversion），让 `FeedbackBus` 依赖于 `OperatorProtocol` 这一抽象接口，而不是具体的资源加载逻辑。

### 标签
#intent/refine #flow/ready #priority/high
#comp/bus #concept/executor #scope/core
#ai/brainstorm
#task/domain/bus
#task/object/feedback-bus
#task/action/refactor
#task/state/begin

---

### Script

#### Acts 1: 删除 MessageStore 及其导出

由于 `MessageStore` 已经确定是设计过度且位置错误的组件，我们将其彻底从 `pyneedle-bus` 中移除。

~~~~~act
delete_file
packages/pyneedle-bus/src/needle/bus/store.py
~~~~~

~~~~~act
patch_file
packages/pyneedle-bus/src/needle/bus/__init__.py
~~~~~
~~~~~python.old
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
    "event_bus",  # The default EventBus singleton
    "message_store",  # The default Store
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
~~~~~python.new
from .event import EventBus, EventHandler
from .feedback import FeedbackBus
from .bridge import LogBridge

__all__ = [
    "EventBus",
    "EventHandler",
    "FeedbackBus",
    "LogBridge",
    "bus",  # The default FeedbackBus singleton
    "event_bus",  # The default EventBus singleton
]

# --- Default Singleton Instances ---
# For simple apps (like CLI tools), a global singleton is often sufficient.
# Complex apps (like Cascade Engine) may instantiate their own buses.

# Note: Renderer and Operator are not set by default.
# The application entry point (CLI/Main) must call:
# - `bus.set_renderer(...)`
# - `bus.set_operator(...)`
bus = FeedbackBus()

event_bus = EventBus()
~~~~~

#### Acts 2: 重构 FeedbackBus 以支持 Operator 注入

修改 `FeedbackBus`，使其不再通过 `MessageStore` 自动处理语言和加载，而是直接使用注入的 `operator`。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/feedback.py
~~~~~
~~~~~python
from typing import Any, Optional, Union

from needle.spec import SemanticPointerProtocol, RendererProtocol, OperatorProtocol


class FeedbackBus:
    """
    The output channel for the application.
    It relies on an injected Operator to resolve Pointers to Templates.
    """

    def __init__(
        self,
        operator: Optional[OperatorProtocol] = None,
        renderer: Optional[RendererProtocol] = None,
    ):
        self._operator = operator
        self._renderer = renderer

    def set_renderer(self, renderer: RendererProtocol) -> None:
        self._renderer = renderer

    def set_operator(self, operator: OperatorProtocol) -> None:
        """Inject the Operator (Nexus) responsible for resolving pointers."""
        self._operator = operator

    def _get_template(self, ptr: Union[str, SemanticPointerProtocol]) -> str:
        # 1. Fallback if no operator is set
        if not self._operator:
            return str(ptr)

        # 2. Lookup template from the operator
        template = self._operator(ptr)

        # 3. Fallback: If not found, stringify the pointer itself
        if template is None:
            return str(ptr)

        return str(template)

    def render_to_string(
        self,
        ptr: Union[str, SemanticPointerProtocol],
        **kwargs: Any,
    ) -> str:
        """
        Resolve a template and format it into a string without rendering.

        Args:
            ptr: Semantic Pointer or string ID of the template.
            **kwargs: Arguments for template formatting.

        Returns:
            The fully formatted message string.
        """
        template = self._get_template(ptr)

        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"<formatting error for '{ptr}': missing key {e}>"
        except Exception as e:
            return f"<rendering error for '{ptr}': {e}>"

    def present(
        self,
        ptr: Union[str, SemanticPointerProtocol],
        level: str = "info",
        **kwargs: Any,
    ) -> None:
        """
        Present a message to the user via the registered renderer.

        Args:
            ptr: Semantic Pointer to the message template (e.g. L.io.file_saved)
            level: 'info', 'success', 'warning', 'error', 'debug'
            **kwargs: Arguments for template formatting
        """
        if not self._renderer:
            return

        message = self.render_to_string(ptr, **kwargs)
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

### 下一步建议

我们已经完成了 `pyneedle-bus` 的“净化”。现在，这个总线非常轻量，它仅仅是一个消息中转站，等待着外部注入 Renderer 和 Operator。

**下一步的任务焦点将转移到 `stitcher-common`**：
我们需要修改 `packages/stitcher-common/src/stitcher/common/bus.py`。目前的版本还试图调用 `message_store.register_asset_root`，这会报错。我们需要在那里：
1.  **手动检测语言**（使用原 `MessageStore` 中的静态逻辑或通过环境变量）。
2.  **实例化 `I18NFactoryOperator`**。
3.  **构建 `OverlayOperator`**（将 Stitcher 自身的 Assets 与全局的默认 Operator 层叠）。
4.  **将组装好的 Operator 注入 `bus.set_operator(...)`**。

如果你准备好了，请指示我开始重构 Stitcher 的组装逻辑。
