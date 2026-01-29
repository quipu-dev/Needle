好的，我们现在为 `Needle` 项目创建一个完整的逻辑提交。这次重构彻底理清了总线与资源加载之间的边界，是架构演进中的一个里程碑。

## [COMMIT] refactor(bus): 解构 FeedbackBus 与 MessageStore 的耦合

### 用户需求
为 Needle 项目中 `pyneedle-bus` 的架构重构创建 Git 提交。

### 评论
这次提交标志着 `pyneedle-bus` 正式从一个“带有特定策略的 I18n 工具”进化为一个“纯粹的、接口驱动的消息展示通道”。通过删除 `MessageStore`，我们消除了基础设施层对文件系统的隐式依赖，使得 `FeedbackBus` 可以无缝适应从 CLI 到云端微服务的各种环境。

### 目标
1.  暂存 `pyneedle-bus` 包中的所有变更（包括代码删除、重构和测试更新）。
2.  创建一个详尽的提交说明，记录架构变更的动机和影响。

### 基本原理
遵循 **HFEA v1.0** 的“确定性路径追踪”公理。我们将架构的灵活性（如何加载资源）交还给应用层，并在基础设施层保持绝对的简单和确定性。

### 标签
#intent/refine #flow/ready #priority/medium
#comp/bus #comp/build #comp/tests
#task/domain/bus
#task/object/refactor-feedback-bus
#task/action/commit
#task/state/end #task/status/completed

---

### Script

#### Acts 1: 提交 Needle 变更

我们将暂存 `pyneedle-bus` 相关的修改，并创建一个反映架构深度演进的 Commit。

~~~~~act
git_add
~~~~~

~~~~~act
git_commit
~~~~~
~~~~~text
refactor(bus): decouple FeedbackBus from MessageStore

This commit performs a major architectural cleanup in `pyneedle-bus` by removing the `MessageStore` component and refactoring `FeedbackBus` to rely on explicit dependency injection.

Key Changes:
- DELETED `MessageStore`: Removed the hardcoded asset loading and language detection logic from the bus package.
- REFACTORED `FeedbackBus`: The bus now accepts an `OperatorProtocol` during initialization or via `set_operator()`. It no longer knows how templates are resolved, only that an operator will provide them.
- UPDATED Tests: Re-implemented the unified bus integration tests to demonstrate explicit operator assembly using `I18NFactoryOperator` and `OverlayOperator`.
- BUMPED Version: Updated `pyneedle-bus` to 0.1.1.

This refactoring aligns with the principle of "Mechanism, not Policy". The bus provides the mechanism for message distribution, while the application (e.g., Stitcher) defines the policy for resource management.
~~~~~

### 下一步建议

Needle 侧的架构重构已经正式入库。

**接下来的行动建议**：
1.  **验证 Stitcher**：虽然我们已经重写了 `stitcher-common` 的 `bus.py`，但尚未正式提交或在 CLI 中进行最终测试。建议运行 `stitcher --help` 检查是否能正确渲染中文（或系统默认语言）的帮助信息。
2.  **Stitcher 提交**：在验证无误后，我们可以为 Stitcher 项目也创建一个对应的 `[COMMIT]` 计划，以保持两个项目在架构步调上的一致性。
