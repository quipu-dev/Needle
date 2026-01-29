我们已经完成了从底层协议到上层分发版的全面升级。这次重构不仅修复了嵌套索引的 Bug，更重要的是为 `pyneedle` 引入了一个简洁、强大的数学模型：**单子化广播（Monadic Broadcasting）**。

现在，我将生成最终的 `[COMMIT]` 计划，将这些变更作为系统的一个稳定基准点进行持久化。

## [COMMIT] refactor: 实现单子化广播 PointerSet 并同步系统版本

### 用户需求
提交 `PointerSet` 的单子化重构、`Spec` 的运行时检查增强，以及全系统的版本同步变更。

### 评论
这是一次深思熟虑的架构进化。通过将“广播”与“展平”定义为 `PointerSet` 的元操作，我们不仅消除了代码中的特殊处理逻辑（Special Cases），还使得复杂的语义代数操作表现得如同“自然规律”般一致。

### 目标
1.  提交 `pyneedle-spec` 中受 `@runtime_checkable` 保护的协议定义。
2.  提交 `pyneedle-pointer` 中基于 `_broadcast` 引擎重构的 `PointerSet` 实现。
3.  提交所有受影响包的版本提升与依赖约束更新。

### 基本原理
我们遵循了 **HFEA v1.0** 的“不可腐蚀性”原则。当发现原有的“战术修复”方案会导致逻辑支离破碎时，我们选择了推翻重来，构建了一个在数学上更完备的“单子化”模型。同步提升版本号则保证了 Monorepo 内各个组件在依赖链条上的确定性。

### 标签
#intent/refine #flow/ready #priority/high 
#comp/spec #comp/runtime #concept/state #scope/core 
#ai/brainstorm 
#task/domain/logic #task/object/pointer-algebra #task/action/refactor
#task/state/end #task/status/completed

---

### Script

#### Acts 1: 提交全系统变更

我们将添加所有修改过的文件并创建一个具有深度上下文的 Git 提交。

~~~~~act
git_add
packages/pyneedle-spec/src/needle/spec/protocols.py
packages/pyneedle-spec/pyproject.toml
packages/pyneedle-pointer/src/needle/pointer/set.py
packages/pyneedle-pointer/tests/test_pointer_algebra.py
packages/pyneedle-pointer/pyproject.toml
packages/pyneedle-runtime/pyproject.toml
packages/pyneedle-bus/pyproject.toml
packages/pyneedle/pyproject.toml
~~~~~

~~~~~act
git_commit
~~~~~
~~~~~text
refactor(pointer): implement Monadic Broadcasting for PointerSet

This commit introduces a significant architectural refinement to the Semantic Pointer algebra, shifting PointerSet from manual logic handling to a unified "Broadcast & Flatten" (Monadic) model.

Key Changes:
1. Spec (v0.1.3): Added @runtime_checkable to all core protocols (SemanticPointerProtocol, etc.) to enable reliable type-sensing within the broadcasting engine.
2. Pointer (v0.1.4):
   - Refactored PointerSet to use a centralized _broadcast engine.
   - Implemented automatic flattening: operations returning collections (dimension expansion) are automatically merged, while atomic moves are added.
   - This emergent behavior naturally handles Cartesian products (PS * PS) and complex nested indexing (L['a','b'][0][1,2]) without special-case logic.
3. System Sync:
   - Synchronized versions for pyneedle-runtime (v0.1.3), pyneedle-bus (v0.1.3), and pyneedle (v0.1.5).
   - Updated internal dependency constraints to lock to the new Spec and Pointer versions.

This refactor eliminates 'Unhashable type: PointerSet' errors and aligns the behavior of PointerSet perfectly with SemanticPointer.
~~~~~

### 下一步建议
- **CI 验证**: 建议在持续集成环境中运行全量测试，确保版本同步没有破坏任何跨包的集成逻辑。
- **文档更新**: 既然 `PointerSet` 的行为已经“单子化”，可以在开发者文档中通过笛卡尔积的例子来展示这一优雅的特性。
- **能力释放**: 这种强大的广播能力现在可以被用于 `pyneedle-bus`，实现更复杂的多路事件监听和反馈分发。
