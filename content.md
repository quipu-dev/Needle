现在，我们将之前的修复和版本更新持久化到 Git 历史中。

这是一个逻辑完整的工作单元：修复了 `PointerSet` 的代数一致性问题，增加了回归测试，并同步更新了版本号。

## [COMMIT] fix(pointer): 支持 PointerSet 的多索引广播与版本更新

### 错误分析

之前，`PointerSet.__getitem__` 在接收到元组索引（例如 `[1, 2]`）时，会触发广播逻辑。由于元组索引会让每个成员返回一个新的 `PointerSet`，而 `PointerSet` 作为子类是不可哈希的（Unhashable），这导致构造父类 `set` 时抛出 `TypeError`。

此外，这在语义上也造成了嵌套集合的错误结果，而非预期的展平集合。

### 用户需求
提交 `PointerSet` 的多索引支持修复及其版本更新。

### 评论
这次提交完善了 `pyneedle` 核心代数逻辑中的一个关键边缘场景，确保了在大规模语义路由和配置分发时的稳定性。

### 目标
1.  将修复后的代码、新增的测试用例以及版本更新添加到 Git 暂存区。
2.  创建一个清晰、详尽的提交记录。

### 基本原理
通过将逻辑修复与版本号更新打包在一个提交中，我们确保了代码仓库的每一个版本点都是功能完备且自洽的。

### 标签
#intent/fix #flow/ready #priority/high
#comp/runtime #concept/state #scope/core
#ai/instruct
#task/domain/logic #task/object/pointer-algebra #task/action/fix
#task/state/end #task/status/completed

---

### Script

#### Acts 1: 提交变更

我们将相关文件添加到暂存区并提交。

~~~~~act
git_add
packages/pyneedle-pointer/src/needle/pointer/set.py
packages/pyneedle-pointer/tests/test_pointer_algebra.py
packages/pyneedle-pointer/pyproject.toml
~~~~~

~~~~~act
git_commit
~~~~~
~~~~~text
fix(pointer): support multi-index broadcasting on PointerSet

Fixed a 'TypeError: unhashable type: PointerSet' that occurred when using multiple indices on a PointerSet instance (e.g., L['a','b'][0][1,2]).

The issue was caused by PointerSet.__getitem__ attempting to broadcast a tuple index to its members. Since a tuple index on a SemanticPointer returns a PointerSet, the resulting collection became a 'set of sets', which failed because sets are not hashable.

Updated PointerSet.__getitem__ to intercept tuple indices and redirect them to the multiplication/distribution logic (self * key). This ensures that multi-indices are correctly flattened into a single PointerSet, maintaining algebraic consistency with SemanticPointer.

Changes:
- Modified needle.pointer.set.PointerSet.__getitem__ to handle tuple keys.
- Added regression test 'test_pointer_set_complex_nested_multi_index'.
- Bumped pyneedle-pointer version to 0.1.3.
~~~~~

### 下一步建议
- **同步分发**: 如果你使用了 `uv` 或是其他包管理工具，建议运行同步命令以确保环境中的版本号已更新。
- **架构审查**: 既然核心代数逻辑已稳固，下一步可以考虑继续完善 `pyneedle-bus` 对复杂 `PointerSet` 路由的支持。
