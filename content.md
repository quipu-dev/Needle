这是一个非常合理的补全。既然 `PointerSet` 已经支持了属性访问（`.`）和算术运算符（`/`, `+`）的广播，那么索引访问（`[]`）也应该遵循同样的逻辑。

这将允许像 `L['auth', 'api'][0].fail` 这样的组合语法，将其广播为 `{L.auth[0].fail, L.api[0].fail}`。

## [WIP] feat(pointer): 为 PointerSet 实现索引访问的广播支持

### 用户需求
增强 `PointerSet` 的一致性：使 `PointerSet[key]` 能够将其索引操作广播到集合中的每一个 `SemanticPointer`。

### 评论
通过实现 `__getitem__` 广播，我们完成了 `PointerSet` 对 `SemanticPointer` 所有主要导航方式的镜像。这使得集合操作在语义上完全透明——用户可以像操作单个指针一样操作指针集合，而无需显式编写循环。

### 目标
1. 修改 `packages/pyneedle-pointer/src/needle/pointer/set.py` 以支持 `__getitem__`。
2. 更新 `packages/pyneedle-spec/src/needle/spec/protocols.py` 以在协议中体现此能力。
3. 在测试文件中增加验证用例。

### 基本原理
在 `PointerSet` 中定义 `__getitem__`，它会遍历集合中的每个指针 `p`，调用 `p[key]`，并将结果收集到一个新的 `PointerSet` 中。这与 `__getattr__` 的逻辑高度一致。

### 标签
#intent/refine #flow/ready #priority/medium
#comp/pointer #comp/spec #concept/navigation #scope/ux
#ai/instruct
#task/domain/pointer #task/object/pointer-set #task/action/refactor
#task/state/continue

---

### Script

#### Acts 1: 在 `PointerSetProtocol` 中定义索引能力

首先，我们在规格层确保 `PointerSet` 被定义为可索引的。

~~~~~act
patch_file
packages/pyneedle-spec/src/needle/spec/protocols.py
~~~~~
~~~~~python.old
    def __add__(
        self, other: Union[str, SemanticPointerProtocol]
    ) -> "PointerSetProtocol": ...

    def __mul__(self, other: Any) -> "PointerSetProtocol": ...
~~~~~
~~~~~python.new
    def __add__(
        self, other: Union[str, SemanticPointerProtocol]
    ) -> "PointerSetProtocol": ...

    def __mul__(self, other: Any) -> "PointerSetProtocol": ...

    def __getitem__(self, key: Any) -> "PointerSetProtocol": ...
~~~~~

#### Acts 2: 在 `PointerSet` 中实现 `__getitem__` 广播

接下来，在实现层完成逻辑。

~~~~~act
patch_file
packages/pyneedle-pointer/src/needle/pointer/set.py
~~~~~
~~~~~python.old
class PointerSet(Set["SemanticPointer"], PointerSetProtocol):
    def __getattr__(self, name: str) -> "PointerSet":
        # Broadcast attribute access to all pointers in the set.
        # This allows L.api["v1", "v2"].users syntax.
        return self / name

    def __truediv__(self, other: Union[str, "SemanticPointerProtocol"]) -> "PointerSet":
~~~~~
~~~~~python.new
class PointerSet(Set["SemanticPointer"], PointerSetProtocol):
    def __getattr__(self, name: str) -> "PointerSet":
        # Broadcast attribute access to all pointers in the set.
        # This allows L.api["v1", "v2"].users syntax.
        return self / name

    def __getitem__(self, key: Any) -> "PointerSet":
        # Broadcast indexing to all pointers in the set.
        # This allows L["a", "b"][0] -> {L.a[0], L.b[0]}
        return PointerSet(p[key] for p in self)

    def __truediv__(self, other: Union[str, "SemanticPointerProtocol"]) -> "PointerSet":
~~~~~

#### Acts 3: 增加索引广播的测试用例

在测试文件中验证这一新行为。

~~~~~act
patch_file
packages/pyneedle-pointer/tests/test_pointer_algebra.py
~~~~~
~~~~~python.old
    # Chaining after wildcard
    p3 = L.check["+"] / "error"
    assert str(p3) == "check.+.error"
~~~~~
~~~~~python.new
    # Chaining after wildcard
    p3 = L.check["+"] / "error"
    assert str(p3) == "check.+.error"


def test_pointer_set_getitem_broadcasting():
    # Test broadcasting of __getitem__ on a PointerSet
    ps = L["auth", "api"][0]
    assert ps == {L.auth[0], L.api[0]}

    # Combined complex chaining
    ps2 = L["http", "ftp"].v1[404].detail
    assert ps2 == {L.http.v1[404].detail, L.ftp.v1[404].detail}
~~~~~

### 下一步建议
- **执行测试**: 请运行 `pytest packages/pyneedle-pointer/tests/test_pointer_algebra.py`。
- **架构审查**: 现在的 `L` 指针代数已经非常完备了。如果你对这套语法感到满意，我们可以考虑将其作为 `0.1.4` 版本的核心特性进行一次提交。
