好的，我们已经完成了 `pyneedle-bus` 的核心开发、测试以及 Bug 修复。现在这个包已经处于一个稳定、一致且经过验证的状态。

我将生成一个 `[COMMIT]` 计划，将这些变更作为一个完整的逻辑单元提交到 `Needle` 仓库。

## [COMMIT] feat: implement unified pyneedle-bus architecture

### 用户需求

在 `Needle` 仓库中正式提交统一总线架构的实现。

### 评论

这是一个具有里程碑意义的提交。我们不仅成功地在 `pyneedle-bus` 中实现了 EventBus（神经系统）和 FeedbackBus（表达系统）的解耦与统一，还通过复用 `pyneedle-runtime` 的 Operator 体系，实现了一个极其优雅且强大的资源管理层（MessageStore）。集成测试的通过证明了这一架构在处理多层 I18n 覆盖、语言切换以及事件桥接方面的健壮性。这为整个 PyNeedle 生态系统的“去中心化总线”战略打下了坚实的底座。

### 目标

1.  将所有与 `pyneedle-bus` 相关的代码、规范更新、配置变更和测试用例添加到 Git 暂存区。
2.  创建一个详尽的提交记录，阐述本次架构变革的核心内容。

### 基本原理

遵循 `d3-constraint-quipu-plan-script-rules` 指令级约束，本计划仅包含 Git 操作（`git_add` 和 `git_commit`），不包含任何文件系统修改。我们将按组件对文件进行归类添加，以确保提交的完整性。

### 标签

#intent/build #flow/ready #priority/high #comp/bus #comp/spec #comp/build #concept/event #concept/i18n #scope/core #ai/delegate #task/domain/bus #task/object/core-implementation #task/action/implementation #task/state/end #task/status/completed

---

### Script

#### Acts 1: 提交 pyneedle-bus 架构实现

我们将所有变更添加到暂存区并提交。

~~~~~act
git_add
packages/pyneedle-bus/pyproject.toml
packages/pyneedle-bus/src/needle/__init__.py
packages/pyneedle-bus/src/needle/bus/__init__.py
packages/pyneedle-bus/src/needle/bus/event.py
packages/pyneedle-bus/src/needle/bus/store.py
packages/pyneedle-bus/src/needle/bus/feedback.py
packages/pyneedle-bus/src/needle/bus/bridge.py
packages/pyneedle-bus/tests/test_unified_bus.py
packages/pyneedle-spec/src/needle/spec/events.py
packages/pyneedle-spec/src/needle/spec/protocols.py
packages/pyneedle-spec/src/needle/spec/__init__.py
packages/pyneedle/pyproject.toml
pyproject.toml
~~~~~

~~~~~act
git_commit
~~~~~
~~~~~text
feat: implement unified pyneedle-bus architecture

This commit introduces the 'pyneedle-bus' package, providing a unified backbone for the ecosystem by separating logical signaling (EventBus) from user-facing feedback (FeedbackBus).

Key Implementation Details:
- EventBus: A high-performance logic bus that supports routing via strings, Semantic Pointers (L), and class types.
- MessageStore: An orchestrator that leverages the 'pyneedle-runtime' Operator system. It manages multiple asset roots and builds a prioritized OverlayOperator for zero-IO I18n resource management.
- FeedbackBus: A presentation layer that resolves Semantic Pointers to localized templates and delegates rendering to pluggable backends.
- LogBridge: A core component that enables 'Zero-Config Logging' by bridging Event topics directly to Feedback pointers.

Specifications (pyneedle-spec):
- GenericEventIR: A minimalist, serializable event envelope.
- RendererProtocol: A standardized interface for TUI/CLI output backends.

The package is fully integrated into the monorepo, type-checked with Pyright, and verified via a comprehensive integration test covering multi-root i18n overlays and event-to-feedback bridging.
~~~~~

### 下一步建议

随着 `pyneedle-bus` 的归位，我们已经准备好进行下一步的“边缘绞杀”。我建议接下来的操作顺序如下：

1.  **Stitcher 改造**: 进入 `Stitcher` 仓库，删除其原有的 `stitcher-bus` 包，并重构其代码以直接依赖 `pyneedle-bus`。这是验证“心脏移植”策略可行性的最佳切入点。
2.  **Quipu 改造**: 紧接着对 `Quipu` 进行类似的重构，特别是将其 TUI 渲染逻辑与 `FeedbackBus` 对接。
3.  **Cascade 改造**: 最后处理 `Cascade`，这将涉及最大规模的事件类重构，使其兼容 `GenericEventIR` 规范。

您是否准备好先从 `Stitcher` 开始？
