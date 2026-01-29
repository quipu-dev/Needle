好的。所有的功能实现、测试验证以及版本同步工作已经完成。现在我将生成一个提交计划，将这些更改正式持久化到 Git 历史中。

## [COMMIT] feat(pointer): 支持 L 指针的多重索引与 PointerSet 的广播操作

### 用户需求
正式提交对 `SemanticPointer` 和 `PointerSet` 的增强功能，包括：
1. `L['a', 'b']` 快捷创建集合。
2. `L['+']` 模式构造支持。
3. `PointerSet` 的属性与索引广播。
4. 协议更新与版本同步。

### 评论
这是一次具有里程碑意义的提交。它不仅极大地提升了 `PyNeedle` DSL 的表达力，还为后续在总线层实现基于通配符的“模糊路由”奠定了坚实的语法基础。通过同步提升版本号，我们确保了生态系统内各组件的契约一致性。

### 目标
1. 将所有修改过的源文件、测试文件和配置文件添加到暂存区。
2. 创建一个符合 Conventional Commits 规范的、详细的提交信息。

### 基本原理
遵循 `d3-constraint-quipu-plan-script-rules-D3-P2` 协议，本计划仅包含 Git 操作，确保提交动作的原子性和纯粹性。

### 标签
#intent/tooling #flow/ready #priority/medium
#comp/pointer #comp/spec #comp/build #scope/api
#ai/instruct
#task/domain/pointer #task/object/pointer-algebra #task/action/commit
#task/state/end #task/status/completed

---

### Script

#### Acts 1: 提交变更

我们将所有涉及到的文件添加并提交。

~~~~~act
git_add
packages/pyneedle-spec/src/needle/spec/protocols.py
packages/pyneedle-spec/pyproject.toml
packages/pyneedle-pointer/src/needle/pointer/core.py
packages/pyneedle-pointer/src/needle/pointer/set.py
packages/pyneedle-pointer/tests/test_pointer_algebra.py
packages/pyneedle-pointer/pyproject.toml
packages/pyneedle-bus/pyproject.toml
packages/pyneedle-runtime/pyproject.toml
packages/pyneedle/pyproject.toml
~~~~~

~~~~~act
git_commit
~~~~~
~~~~~text
feat(pointer): support multi-indexing and broadcasting for L and PointerSet

This commit introduces significant enhancements to the Semantic Pointer algebra,
improving its expressiveness and usability in complex routing scenarios.

Core Changes:
- SemanticPointer: Enhanced `__getitem__` to support multi-indexing.
  `L['a', 'b']` now returns a `PointerSet` (shortcut for `L * ['a', 'b']`).
  Single index `L['+']` remains a `SemanticPointer` for pattern/wildcard construction.
- PointerSet: Implemented attribute broadcasting (`__getattr__`) and indexing
  broadcasting (`__getitem__`). This allows fluent chaining like
  `L.api['v1', 'v2'].users` or `L['a', 'b'][0].fail`.
- Spec: Updated `SemanticPointerProtocol` and `PointerSetProtocol` to reflect
  the new polymorphic indexing and broadcasting capabilities.

Versioning & Tooling:
- Synchronized version numbers across the monorepo (sub-packages to 0.1.2,
  meta-package to 0.1.4).
- Added comprehensive unit tests for the new indexing and broadcasting behaviors.

These changes provide the syntactic foundation for implementing MQTT-style
wildcard matching in the FeedbackBus/EventBus.
~~~~~

### 下一步建议
- **总线重构**: 随着语法基础的就绪，我们下一步可以开始重构 `pyneedle-bus` 中的 `EventBus` 和 `FeedbackBus`，利用 `L['+']` 和 `L['#']` 实现高效的主题匹配逻辑。
- **文档更新**: 建议更新项目 README，向用户展示 `L['a', 'b']` 这种更优雅的集合创建语法。
