由于 `MessageStore` 已被移除，我们必须更新测试用例，使其遵循新的“显式组装”模式。在测试中，我们将手动实例化 `I18NFactoryOperator` 和 `OverlayOperator` 并注入到 `FeedbackBus` 中。

这实际上让测试变得更清晰了，因为它展示了如何在没有硬编码存储逻辑的情况下，通过组合不同的 `Operator` 来实现相同的 I18n 功能。

## [WIP] test(bus): 更新统一总线测试以适配 Operator 注入架构

### 用户需求
修复因 `MessageStore` 被删除而导致的 `pyneedle-bus` 测试失败。

### 评论
这次重构虽然增加了测试代码的行数（因为我们需要手动组装 Operator），但它验证了 `FeedbackBus` 的核心接口已经变得足够通用。我们现在是在测试“组装好的总线”如何工作，而不是测试总线内部那个黑盒存储。

### 目标
1.  **修改** `packages/pyneedle-bus/tests/test_unified_bus.py`：
    *   移除 `MessageStore` 导入。
    *   从 `needle.operators` 导入所需的 `I18NFactoryOperator` 和 `OverlayOperator`。
    *   更新 `test_unified_bus_integration`，手动创建并注入 `Operator` 链。
    *   由于 `FeedbackBus` 不再自动响应 `monkeypatch` 的环境变量（因为它不再持有检测逻辑），测试中需要手动切换 Operator 以验证不同语言的渲染。

### 标签
#intent/refine #flow/ready #priority/high
#comp/bus #comp/tests #scope/core
#task/domain/testing
#task/object/bus-tests
#task/action/update
#task/state/continue

---

### Script

#### Acts 1: 更新测试用例

我们将重写集成测试。由于我们追求“高保真”，测试将模拟应用启动时的真实行为：扫描路径、创建工厂、组合层叠。

~~~~~act
write_file
packages/pyneedle-bus/tests/test_unified_bus.py
~~~~~
~~~~~python
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

import pytest
from needle.pointer import L
from needle.spec import RendererProtocol

# From bus
from needle.bus import (
    EventBus,
    FeedbackBus,
    LogBridge,
)

# From runtime/operators (integration test)
from needle.operators import I18NFactoryOperator, OverlayOperator


# --- Fixtures ---


class SpyRenderer(RendererProtocol):
    """A mock renderer that captures calls instead of printing."""

    def __init__(self):
        self.calls: List[Tuple[str, str, Dict[str, Any]]] = []

    def render(self, message: str, level: str = "info", **kwargs: Any) -> None:
        self.calls.append((message, level, kwargs))

    def get_last_message(self) -> str:
        return self.calls[-1][0] if self.calls else ""

    def clear(self):
        self.calls.clear()


@pytest.fixture
def mock_asset_structure(tmp_path: Path) -> Dict[str, Path]:
    """Creates a mock filesystem structure for testing i18n overlays."""
    # 1. Core App Assets (Low Priority)
    app_root = tmp_path / "app_assets"
    app_en_dir = app_root / "needle" / "en"
    app_zh_dir = app_root / "needle" / "zh"
    app_en_dir.mkdir(parents=True)
    app_zh_dir.mkdir(parents=True)

    app_en_data = {
        "welcome": "Welcome to CoreApp!",
        "setup": "Initializing system...",
    }
    app_zh_data = {
        "welcome": "欢迎使用核心应用！",
        "setup": "正在初始化系统...",
    }
    (app_en_dir / "app.json").write_text(json.dumps(app_en_data))
    (app_zh_dir / "app.json").write_text(json.dumps(app_zh_data, ensure_ascii=False))

    # 2. Plugin Assets (High Priority)
    plugin_root = tmp_path / "plugin_assets"
    plugin_en_dir = plugin_root / "needle" / "en"
    plugin_zh_dir = plugin_root / "needle" / "zh"
    plugin_en_dir.mkdir(parents=True)
    plugin_zh_dir.mkdir(parents=True)

    plugin_en_data = {
        "welcome": "Welcome from MyPlugin!",  # Override
        "farewell": "Goodbye from Plugin!",  # New
    }
    plugin_zh_data = {
        "welcome": "MyPlugin 欢迎您！",
        "farewell": "插件再见！",
    }
    (plugin_en_dir / "app.json").write_text(json.dumps(plugin_en_data))
    (plugin_zh_dir / "app.json").write_text(
        json.dumps(plugin_zh_data, ensure_ascii=False)
    )

    return {"app": app_root, "plugin": plugin_root}


# --- Test Cases ---


def test_unified_bus_integration(mock_asset_structure):
    """
    End-to-end test for the entire pyneedle-bus stack with manually assembled operators.
    """
    # 1. ARRANGE
    event_bus = EventBus()
    spy_renderer = SpyRenderer()
    feedback_bus = FeedbackBus(renderer=spy_renderer)
    bridge = LogBridge(event_bus, feedback_bus)

    # Manual Operator Assembly
    # Later roots override earlier ones? OverlayOperator uses first-match-wins.
    # So we put [Plugin, App] to let Plugin override App.
    app_factory = I18NFactoryOperator(mock_asset_structure["app"])
    plugin_factory = I18NFactoryOperator(mock_asset_structure["plugin"])

    def set_language(lang: str):
        # Build a specific overlay for the target language
        # plugin_factory(lang) returns a FileSystemOperator for that dir
        overlay = OverlayOperator([plugin_factory(lang), app_factory(lang)])
        feedback_bus.set_operator(overlay)

    # Connect the bridge
    bridge.connect(L.app.farewell, level="success")

    # 2. ACT & ASSERT: FeedbackBus direct rendering

    # Test English
    set_language("en")
    feedback_bus.info(L.app.welcome)
    assert spy_renderer.get_last_message() == "Welcome from MyPlugin!"

    # Test English - Fallback (found in App but not in Plugin)
    feedback_bus.info(L.app.setup)
    assert spy_renderer.get_last_message() == "Initializing system..."

    spy_renderer.clear()

    # Test Chinese
    set_language("zh")
    feedback_bus.warning(L.app.welcome)
    assert spy_renderer.get_last_message() == "MyPlugin 欢迎您！"
    assert spy_renderer.calls[-1][1] == "warning"

    spy_renderer.clear()

    # 3. ACT & ASSERT: EventBus -> Bridge -> FeedbackBus
    set_language("en")

    # Publish an event
    class UserLogoutEvent:
        def __init__(self, username):
            self.username = username
            self.topic = L.app.farewell

    event_bus.publish(UserLogoutEvent(username="Alice"))

    assert len(spy_renderer.calls) == 1
    assert spy_renderer.get_last_message() == "Goodbye from Plugin!"
    assert spy_renderer.calls[0][1] == "success"
~~~~~

### 下一步建议

`pyneedle-bus` 的测试现在应该能通过了。我们已经证明了通过注入外部 Operator，`FeedbackBus` 依然能完美支持 I18n 和层叠覆盖逻辑。

现在，球回到了 **Stitcher** 这边。由于 `pyneedle-bus` 已经不再提供默认的 `MessageStore` 和自动加载功能，`stitcher-common` 必须承担起这个责任。

**下一个任务**：
重构 `packages/stitcher-common/src/stitcher/common/bus.py`，使其包含以下逻辑：
1.  **检测语言**（实现原来的 `MessageStore.detect_lang`）。
2.  **定位资产**。
3.  **组装 `stitcher_operator` (Nexus)**。
4.  **注入全局 `bus` 单例**。

如果你同意，我们将开始处理 Stitcher 的副作用修复。
