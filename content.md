你观察得非常敏锐。在 `pyneedle-bus` 的初始设计中，`FeedbackBus` 确实缺少一个直接返回字符串的方法。为了支持 `Stitcher` 的 `nexus` 操作符（它通常用于将 L 指针动态转换为文本，例如在 CLI 帮助信息或复杂的 UI 拼接中），我们需要在底层补齐这个能力。

根据 `ADAP v1.0` 协议，我将在 `Needle` 仓库中进行此项增强。

## [WIP] feat(bus): 为 FeedbackBus 添加 render_to_string 方法

### 用户需求
在 `FeedbackBus` 中实现 `render_to_string` 方法，允许调用者仅执行模板解析和格式化逻辑，而不触发物理渲染。

### 评论
这是 `FeedbackBus` 功能完备性的重要补充。原本的 `present` 方法耦合了“解析”和“渲染”两个阶段。通过提取出 `render_to_string`，我们不仅满足了 `Stitcher` 的向后兼容性，还为下游项目提供了更灵活的文本处理能力。

### 目标
1.  在 `FeedbackBus` 类中新增 `render_to_string` 方法。
2.  重构 `present` 方法，使其调用 `render_to_string` 以减少代码冗余。
3.  确保错误处理逻辑（KeyError 等）在两个入口点保持一致。

### 基本原理
我们将 `present` 内部的 `template.format` 逻辑提取为一个公共方法。这个方法接收 `ptr` 和 `kwargs`，返回最终的字符串。如果模板不存在，它将回退到 `ptr` 的字符串表示。这符合我们“优雅降级”的设计哲学。

### 标签
#intent/build #flow/ready #priority/high 
#comp/bus #concept/feedback #scope/api
#ai/instruct
#task/domain/bus #task/object/feedback-bus #task/action/refactor #task/state/continue

---

### Script

#### Acts 1: 增强 `FeedbackBus` 实现

我们将修改 `packages/pyneedle-bus/src/needle/bus/feedback.py`，提取并暴露渲染逻辑。

~~~~~act
patch_file
packages/pyneedle-bus/src/needle/bus/feedback.py
~~~~~
~~~~~python.old
    def present(
        self,
        ptr: Union[str, SemanticPointerProtocol],
        level: str = "info",
        **kwargs: Any,
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
~~~~~
~~~~~python.new
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
~~~~~

### 下一步建议
`Needle` 端的补丁已经打好。现在你可以回到 `Stitcher` 目录，之前生成的 `stitcher.common.bus.stitcher_operator` 现在可以正常调用 `bus.render_to_string` 了。

接下来，请在 `Stitcher` 目录下执行之前生成的 `Acts 2` 到 `Acts 5`（全局替换和旧包删除），完成“心脏移植”。完成后，你可以运行 `uv run stitcher --help` 来验证 I18n 资源是否加载成功。
