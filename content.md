这是一个测试逻辑错误。在测试的第二部分，我们将环境变量 `NEEDLE_LANG` 设置为了 `"zh"`，但在第三部分（测试 EventBus）时，注释声称使用 `"EN locale"`，且断言期望的是英文结果 `"Goodbye from Plugin!"`，但代码并没有将语言切回英文，导致实际输出了中文 `"插件再见！"`。

我将修复测试代码，在进入第三部分测试前显式将语言切回英文。

## [WIP] fix: 修复集成测试中的语言环境未重置问题

### 用户需求

修复 `packages/pyneedle-bus/tests/test_unified_bus.py` 中的断言错误。

### 评论

测试失败验证了 I18n 逻辑实际上是**工作正常**的（它正确地在中文环境下输出了中文）。错误在于测试脚本的编排：在验证完中文场景后，未将环境重置回英文，导致后续期望英文输出的断言失败。只需添加一行代码将环境重置即可。

### 目标

1.  修正测试文件，确保在测试 EventBus 桥接功能前，语言环境被正确设置为英文。
2.  确保集成测试通过。

### 基本原理

使用 `patch_file` 在 `spy_renderer.clear()` 和 `3. ACT & ASSERT...` 之间插入 `monkeypatch.setenv("NEEDLE_LANG", "en")`。

### 标签

#intent/fix #flow/ready #priority/medium #comp/tests #scope/core #task/domain/bus #task/object/test-fix #task/action/patch #task/state/end

---

### Script

#### Acts 1: 修复测试文件

在进入第三阶段测试前，显式将语言环境重置为英文。

~~~~~act
patch_file
packages/pyneedle-bus/tests/test_unified_bus.py
~~~~~
~~~~~python
    spy_renderer.clear()

    # 3. ACT & ASSERT: EventBus -> Bridge -> FeedbackBus
~~~~~
~~~~~python
    spy_renderer.clear()

    # Switch back to English for the final test
    monkeypatch.setenv("NEEDLE_LANG", "en")

    # 3. ACT & ASSERT: EventBus -> Bridge -> FeedbackBus
~~~~~

### 下一步建议

现在测试应该可以通过了。通过后，我们就可以正式开始对 `Stitcher` 进行“边缘绞杀”式的改造了。
