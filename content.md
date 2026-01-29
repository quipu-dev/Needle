好的，我将创建一个 **[COMMIT]** 计划，提交所有类型安全相关的修复，并同步版本号。

## [COMMIT] fix: Resolve type safety issues in PointerSet and Operator usage

### 错误分析
不适用。

### 用户需求
提交对 `PointerSet._broadcast` 方法和 `FileSystemOperator` 测试调用中的类型安全修复。同时，由于这是对 `pyneedle-pointer` 和 `pyneedle-spec` 0.2.x/0.1.x 分支的修复，所有依赖包的版本号将相应地同步到最新版本。

### 评论
这次提交通过引入 `typing.cast` 解决了静态分析器对泛型和 Union 类型的误判，确保了 `PointerSet` 在广播操作中只添加 `SemanticPointer` 对象。这提高了整个 `pyneedle` 库的静态类型检查质量。

### 目标
提交以下文件：
1.  `pyneedle-spec/src/needle/spec/protocols.py` (类型协议修正)
2.  `pyneedle-pointer/src/needle/pointer/core.py` (迭代器实现)
3.  `pyneedle-pointer/src/needle/pointer/set.py` (广播类型修正)
4.  `pyneedle-pointer/tests/test_pointer_algebra.py` (新增迭代测试)
5.  `pyneedle-runtime/tests/test_pipeline_integration.py` (Operator 调用类型修正)
6.  所有 `pyproject.toml` 文件中关于版本号的更新（Pointer 0.2.1, Spec 0.1.5）。

### 基本原理
**类型收窄**: 使用 `cast` 解决了 Pyright 无法推断 Union 类型实例具体行为的问题，允许我们在运行时确定的路径中继续编码。
**无限循环修复**: 显式实现 `__iter__` 是防止 `SemanticPointer` 陷入 `__getitem__` 驱动的无限循环的关键修复。

### 标签
#intent/fix #flow/ready #priority/high
#comp/pointer #comp/spec #comp/runtime #comp/build #scope/dx
#ai/delegate
#task/domain/pointer #task/object/type-safety #task/action/fix
#task/state/end #task/status/completed

---

### Script

#### Acts 1: 暂存所有修改的文件

~~~~~act
git_add
packages/pyneedle-spec/src/needle/spec/protocols.py
packages/pyneedle-pointer/src/needle/pointer/core.py
packages/pyneedle-pointer/src/needle/pointer/set.py
packages/pyneedle-pointer/tests/test_pointer_algebra.py
packages/pyneedle-runtime/tests/test_pipeline_integration.py
packages/pyneedle-pointer/pyproject.toml
packages/pyneedle-spec/pyproject.toml
packages/pyneedle/pyproject.toml
~~~~~

#### Acts 2: 创建 Git 提交

~~~~~act
git_commit
~~~~~
~~~~~text
fix(pointer): Prevent infinite iteration and resolve Pyright errors

This commit implements critical fixes for type safety and iteration behavior:

1.  **Infinite Iteration Fix**: `SemanticPointer` now explicitly implements `__iter__` to yield `self`. This prevents Python from falling back to the sequence protocol (`__getitem__(0), __getitem__(1)`) which previously led to an infinite loop due to our dynamic path creation logic (`L.a.b.c.0`, `L.a.b.c.1`, etc.).
2.  **Protocol Correction**: Updated `PointerSetProtocol.__iter__` in `pyneedle-spec` to correctly return `Iterator` instead of `Iterable`, satisfying static analyzers.
3.  **Type Safety Fixes**: Introduced `typing.cast` in `PointerSet._broadcast` and `test_pipeline_integration.py` to correctly narrow the types resulting from polymorphic algebraic operations, thereby resolving Pyright `reportGeneralTypeIssues` warnings.

chore: Bump versions to reflect these important fixes.
*   pyneedle-pointer: 0.2.0 -> 0.2.1
*   pyneedle-spec: 0.1.4 -> 0.1.5
*   pyneedle: 0.1.6 -> 0.1.7 (Minor bump to reflect nested changes)
~~~~~

### 下一步建议
所有已报告的问题均已修复并提交。系统现在处于稳定状态，并且 `SemanticPointer` 的代数 API 既灵活又具有静态类型安全性。你可以开始下一个任务。
