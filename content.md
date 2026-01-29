你是对的。为了让 `L.api["v1", "v2"].users` 这种链式调用生效，`PointerSet` 必须支持**属性访问的广播（Attribute Broadcasting）**。

目前 `PointerSet` 已经支持了 `/` 和 `+` 的广播，补全 `__getattr__` 将使 `PointerSet` 的行为与单体 `SemanticPointer` 在导航语义上完全一致。

## [WIP] feat(pointer): 为 PointerSet 实现属性访问的广播支持

### 用户需求
修复 `PointerSet` 无法通过点号（`.`）进行链式调用的问题。
例如：`L.api["v1", "v2"].users` 应该返回 `{L.api.v1.users, L.api.v2.users}`。

### 评论
这是“最小惊讶原则”的体现。既然 `SemanticPointer` 可以通过属性访问来深入路径，那么作为其集合形式的 `PointerSet` 也理应支持同样的语法，并将其广播到内部的所有指针上。

### 目标
1. 修改 `packages/pyneedle-pointer/src/needle/pointer/set.py`。
2. 为 `PointerSet` 类添加 `__getattr__` 方法。

### 基本原理
在 `PointerSet` 中实现 `__getattr__`，其逻辑非常直接：将属性获取请求转发给内部的每个 `SemanticPointer`。由于 `PointerSet` 已经实现了 `__truediv__`（即 `/` 操作），我们可以直接复用 `self / name` 来实现这一行为。

### 标签
#intent/refine #flow/ready #priority/high
#comp/pointer #concept/navigation #scope/ux #scope/dx
#ai/instruct
#task/domain/pointer #task/object/pointer-set #task/action/refactor
#task/state/continue

---

### Script

#### Acts 1: 在 `PointerSet` 中实现属性访问广播

我们将修改 `set.py`，添加 `__getattr__` 方法。这个方法会在尝试访问 `PointerSet` 自身不存在的属性（如 `.users`）时被触发。

~~~~~act
patch_file
packages/pyneedle-pointer/src/needle/pointer/set.py
~~~~~
~~~~~python.old
class PointerSet(Set["SemanticPointer"], PointerSetProtocol):
    def __truediv__(self, other: Union[str, "SemanticPointerProtocol"]) -> "PointerSet":
        # We assume elements are SemanticPointers which support __truediv__
        return PointerSet(p / other for p in self)
~~~~~
~~~~~python.new
class PointerSet(Set["SemanticPointer"], PointerSetProtocol):
    def __getattr__(self, name: str) -> "PointerSet":
        # Broadcast attribute access to all pointers in the set.
        # This allows L.api["v1", "v2"].users syntax.
        return self / name

    def __truediv__(self, other: Union[str, "SemanticPointerProtocol"]) -> "PointerSet":
        # We assume elements are SemanticPointers which support __truediv__
        return PointerSet(p / other for p in self)
~~~~~

### 下一步建议
- **再次运行测试**: 现在 `test_pointer_getitem_multi_index` 应该可以顺利通过了。请执行 `pytest packages/pyneedle-pointer/tests/test_pointer_algebra.py`。
- **一致性检查**: 检查 `PointerSet` 是否还需要支持其他 `SemanticPointer` 的操作，例如 `__add__` (目前已支持) 或 `__getitem__` 的广播。如果你认为 `L['a', 'b'][0]` 应该返回 `{L.a[0], L.b[0]}`，我们也应该把 `__getitem__` 的广播也加上。
