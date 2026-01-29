这是一个非常好的提炼。`SemanticPointer.__getitem__` (即 `L[...]`) 的当前实现过于依赖 `tuple` 类型，导致它无法优雅地处理其他可迭代的集合，例如 `list` 或 `set`，进而将集合的 `repr` 字符串错误地拼接为路径。

为了解决这个问题，我将放宽 `__getitem__` 的检查逻辑，使其能够识别任何非字符串/非指针的迭代对象，并将其视为多索引的集合扩展，通过 `__mul__` 运算符进行正确处理。

我将生成一个 **[WIP]** 计划来执行代码修改和对应的测试扩展。

## [WIP] feat: 扩展 SemanticPointer.__getitem__ 以支持非元组可迭代对象

### 错误分析
不适用。这是一个功能增强 (feat) 任务。

### 用户需求
用户需要 `SemanticPointer` 上的索引操作符 (`L[...]`) 能够接受任何非字符串、非指针的可迭代对象（如 `list`, `set`）作为多索引，并返回一个 `PointerSet`，而不是将整个迭代对象的内容字符串化后拼接为单一路径。

### 评论
这是一个对 `pyneedle-pointer` 代数API的重要改进，它消除了一个不必要的限制，使得 `L` 对象的组合能力更加灵活和符合 Python 的直觉。这将提高开发者在处理动态集合键时的体验。

### 目标
1.  修改 `packages/pyneedle-pointer/src/needle/pointer/core.py` 中的 `SemanticPointer.__getitem__` 方法。
2.  更新逻辑，检查 `key` 是否是一个可迭代对象，同时排除 `str`, `bytes` 和 `SemanticPointerProtocol` 的实例。
3.  扩展 `packages/pyneedle-pointer/tests/test_pointer_algebra.py` 中的相关测试，确保新的行为是正确的，特别是对于 `list` 和 `set` 作为索引时。

### 基本原理
在 ACA 运行时协议中，`SemanticPointer` 的核心代数操作依赖于 `*`（乘法，用于集合扩展）和 `[]`（索引，用于路径片段）。为了使 `L[key]` 语法成为 `L * key` 的语法糖，当 `key` 代表多个片段时，它必须被路由到 `__mul__`。

当前只检查 `tuple` 过于局限。通过检查所有非字符串、非指针的可迭代类型，我们可以确保 `L[list_of_keys]` 和 `L * list_of_keys` 具有相同的语义和结果，从而提高 API 的连贯性。

### 标签
#intent/build #flow/ready #priority/high
#comp/pointer #concept/algebra #scope/api #scope/dx
#ai/instruct
#task/domain/pointer #task/object/semantic-pointer #task/action/refinement
#task/state/begin

---

### Script

#### Acts 1: 修改 `core.py` 中的 `SemanticPointer.__getitem__` 逻辑

更新 `__getitem__`，使其将任何非字符串/非指针的可迭代对象视为集合展开操作 (等同于 `self * key`)。

~~~~~act
patch_file
packages/pyneedle-pointer/src/needle/pointer/core.py
~~~~~
~~~~~python.old
    def __getitem__(self, key: Any) -> Union["SemanticPointer", "PointerSetProtocol"]:
        if isinstance(key, tuple):
            # Rule: Multiple indices L['a', 'b'] return a PointerSet.
            # Equivalent to self * key.
            return self * key

        # Rule: Single index L['+'] returns a single SemanticPointer.
        return self._join(str(key))
~~~~~
~~~~~python.new
    def __getitem__(self, key: Any) -> Union["SemanticPointer", "PointerSetProtocol"]:
        # Check if the key is a non-string/non-pointer iterable (excluding bytes)
        # We explicitly exclude SemanticPointerProtocol to prevent infinite recursion
        # if a pointer were somehow passed as a raw key, and to treat single pointers
        # as a singular path segment via self._join(str(key)).
        if isinstance(key, Iterable) and not isinstance(
            key, (str, bytes, SemanticPointerProtocol)
        ):
            # Rule: Multiple indices L[iterable] return a PointerSet.
            # Equivalent to self * key.
            return self * key

        # Rule: Single index L['+'] returns a single SemanticPointer.
        return self._join(str(key))
~~~~~

#### Acts 2: 扩展 `test_pointer_algebra.py` 以验证列表和集合索引

在 `test_pointer_getitem_multi_index` 中新增对 `list` 和 `set` 索引的支持验证，确保它们与 `tuple` 索引产生相同的结果。

~~~~~act
patch_file
packages/pyneedle-pointer/tests/test_pointer_algebra.py
~~~~~
~~~~~python.old
def test_pointer_getitem_multi_index():
    # Multi-index L['a', 'b'] should return a PointerSet
    ps = L["a", "b"]
    assert isinstance(ps, PointerSet)
    assert len(ps) == 2
    assert L.a in ps
    assert L.b in ps

    # Chaining with multi-index: L.api['v1', 'v2'].users
    # This proves broadcasting works after the shortcut creation.
    ps2 = L.api["v1", "v2"].users
    assert ps2 == {L.api.v1.users, L.api.v2.users}
~~~~~
~~~~~python.new
def test_pointer_getitem_multi_index():
    # Multi-index L['a', 'b'] (tuple) should return a PointerSet
    ps_tuple = L["a", "b"]
    assert isinstance(ps_tuple, PointerSet)
    assert len(ps_tuple) == 2
    assert L.a in ps_tuple
    assert L.b in ps_tuple

    # NEW: Multi-index L[['a', 'b']] (list) should return a PointerSet
    ps_list = L[["a", "b"]]
    assert ps_list == ps_tuple

    # NEW: Multi-index L[{'a', 'b'}] (set) should return a PointerSet
    ps_set = L[{"a", "b"}]
    assert ps_set == ps_tuple

    # Chaining with multi-index (tuple): L.api['v1', 'v2'].users
    # This proves broadcasting works after the shortcut creation.
    ps2 = L.api["v1", "v2"].users
    expected_ps = {L.api.v1.users, L.api.v2.users}
    assert ps2 == expected_ps

    # NEW: Chaining with multi-index (list)
    ps3 = L.api[["v1", "v2"]].users
    assert ps3 == expected_ps
~~~~~

### 下一步建议
下一步应该运行测试套件，尤其是 `test_pointer_algebra.py`，以验证 `SemanticPointer` 的代数行为和集合展开逻辑依然健全。

如果你确认这些修改，我将生成一个包含 `git_add` 和 `git_commit` 的**新的**计划，以完成本次工作单元。
