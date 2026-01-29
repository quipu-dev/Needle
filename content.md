这是一次极其关键的发现。

目前的行为被称为 **Legacy Sequence Iteration**。当一个类实现了 `__getitem__` 但没有实现 `__iter__` 时，Python 会尝试从 `0` 开始不断传入索引直到 `IndexError`。由于我们的 `__getitem__` 永远不会抛出 `IndexError`（它只会生成更长的路径），这就创造了一个无限迭代器。

正如你所说，实施方案 A（显式定义 `__iter__`）不仅是为了类型安全，更是为了**切断**这个隐式的无限循环，将其行为锁定为安全的“单元素迭代”。

我将生成一个 **[WIP]** 计划来修复此严重缺陷。

## [WIP] fix: 修复 SemanticPointer 的无限迭代并优化静态分析

### 错误分析
当前 `SemanticPointer` 实现了 `__getitem__` 但未实现 `__iter__`。这触发了 Python 的后备迭代机制：尝试 `__getitem__(0)`, `__getitem__(1)`... 由于 `L[int]` 被定义为路径拼接，这导致 `for i in L` 变成了一个无限循环，不断生成数字后缀的子指针。

此外，由于 `PointerSetProtocol.__iter__` 错误地声明返回 `Iterable` 而非 `Iterator`，Pyright 等静态分析工具无法正确识别其可迭代性。

### 用户需求
1.  消除 `for i in L` 导致的无限循环。
2.  让 `SemanticPointer` 表现为长度为 1 的可迭代对象 (`yield self`)。
3.  修正 Protocol 定义以消除静态分析报错。
4.  保留 `SemanticPointer` 的可哈希性。

### 评论
这是一个必须立即修复的阻断性问题。显式实现 `__iter__` 是一石二鸟的方案：它既阻止了灾难性的无限循环，又赋予了 `SemanticPointer` 和 `PointerSet` 统一的迭代接口（多态性），使得类型检查器满意。

### 目标
1.  在 `packages/pyneedle-spec` 中修正 `PointerSetProtocol` 和 `SemanticPointerProtocol`。
2.  在 `packages/pyneedle-pointer` 中为 `SemanticPointer` 实现 `__iter__`。
3.  添加测试用例，证明 `list(L)` 长度为 1，且不会陷入死循环。
4.  提升版本号至 `0.2.1`。

### 基本原理
根据 Python 数据模型，显式的 `__iter__` 优先级高于基于 `__getitem__` 的序列迭代。通过定义 `__iter__` 产生 `self`，我们将 `L` 定义为一个“原子容器”，这符合其在代数操作中的角色（作为集合运算中的单子）。

### 标签
#intent/fix #flow/ready #priority/critical
#comp/pointer #comp/spec #scope/api #concept/algebra
#ai/instruct
#task/domain/pointer #task/object/iteration #task/action/fix
#task/state/continue

---

### Script

#### Acts 1: 修正 Protocol 定义

修正 `protocols.py` 中的类型定义，使其符合 Python 的 `collections.abc` 标准。

~~~~~act
patch_file
packages/pyneedle-spec/src/needle/spec/protocols.py
~~~~~
~~~~~python.old
from typing import Protocol, Any, Union, Iterable, TypeVar, runtime_checkable

# T_co is covariant, meaning SemanticPointerProtocol can return subtypes of itself
T_Pointer = TypeVar("T_Pointer", bound="SemanticPointerProtocol", covariant=True)


@runtime_checkable
class SemanticPointerProtocol(Protocol[T_Pointer]):
    def __getattr__(self, name: str) -> T_Pointer: ...

    def __str__(self) -> str: ...
~~~~~
~~~~~python.new
from typing import Protocol, Any, Union, Iterable, Iterator, TypeVar, runtime_checkable

# T_co is covariant, meaning SemanticPointerProtocol can return subtypes of itself
T_Pointer = TypeVar("T_Pointer", bound="SemanticPointerProtocol", covariant=True)


@runtime_checkable
class SemanticPointerProtocol(Protocol[T_Pointer]):
    # Iterating a single pointer yields itself (Iterator of 1 item)
    def __iter__(self) -> Iterator[T_Pointer]: ...

    def __getattr__(self, name: str) -> T_Pointer: ...

    def __str__(self) -> str: ...
~~~~~

~~~~~act
patch_file
packages/pyneedle-spec/src/needle/spec/protocols.py
~~~~~
~~~~~python.old
@runtime_checkable
class PointerSetProtocol(Protocol):
    def __iter__(self) -> Iterable[SemanticPointerProtocol]: ...

    def __getattr__(self, name: str) -> "PointerSetProtocol": ...
~~~~~
~~~~~python.new
@runtime_checkable
class PointerSetProtocol(Protocol):
    def __iter__(self) -> Iterator[SemanticPointerProtocol]: ...

    def __getattr__(self, name: str) -> "PointerSetProtocol": ...
~~~~~

#### Acts 2: 实现 `SemanticPointer.__iter__`

在 `core.py` 中实现迭代器。同时需要引入 `Iterator` 类型。

~~~~~act
patch_file
packages/pyneedle-pointer/src/needle/pointer/core.py
~~~~~
~~~~~python.old
from typing import Any, Union, Iterable, TYPE_CHECKING
from needle.spec import SemanticPointerProtocol, PointerSetProtocol

if TYPE_CHECKING:
    pass


class SemanticPointer(SemanticPointerProtocol):
    __slots__ = ("_path",)

    def __init__(self, path: str = ""):
        # Internal storage of the dot-separated path
        self._path = path

    def __getattr__(self, name: str) -> "SemanticPointer":
~~~~~
~~~~~python.new
from typing import Any, Union, Iterable, Iterator, TYPE_CHECKING
from needle.spec import SemanticPointerProtocol, PointerSetProtocol

if TYPE_CHECKING:
    pass


class SemanticPointer(SemanticPointerProtocol):
    __slots__ = ("_path",)

    def __init__(self, path: str = ""):
        # Internal storage of the dot-separated path
        self._path = path

    def __iter__(self) -> Iterator["SemanticPointer"]:
        """
        Yield self.
        This prevents Python from falling back to __getitem__ based iteration,
        which would cause an infinite loop (L[0], L[1]...) as we support L[Any].
        It also allows L to be treated as a unitary collection in loops.
        """
        yield self

    def __getattr__(self, name: str) -> "SemanticPointer":
~~~~~

#### Acts 3: 增加测试用例

在 `test_pointer_algebra.py` 中添加关于迭代行为和 Hash 稳定性的测试。

~~~~~act
patch_file
packages/pyneedle-pointer/tests/test_pointer_algebra.py
~~~~~
~~~~~python.old
    ps3 = L / (1, (2,))
    assert ps3 == ps1
~~~~~
~~~~~python.new
    ps3 = L / (1, (2,))
    assert ps3 == ps1


def test_pointer_iteration_is_safe_and_unitary():
    # Regression Test for Infinite Loop Bug
    # Previously, iterating L would fall back to __getitem__(0...inf)
    p = L.a.b.c
    
    # 1. Verify iteration yields only self
    items = list(p)
    assert len(items) == 1
    assert items[0] is p
    
    # 2. Verify hashability is preserved
    # (Implementing __iter__ shouldn't break __hash__ for immutable objects)
    d = {p: "value"}
    assert d[p] == "value"


def test_pointer_static_analysis_duality():
    # This test verifies that we can treat Union[Pointer, PointerSet] uniformly
    # in a loop, simulating what static analysis expects.
    
    def process_items(items: Union[SemanticPointer, PointerSet]):
        count = 0
        for item in items:
            assert isinstance(item, SemanticPointer)
            count += 1
        return count

    # Case 1: Single Pointer
    assert process_items(L.single) == 1
    
    # Case 2: Pointer Set
    assert process_items(L.multiple * {"a", "b"}) == 2
~~~~~

#### Acts 4: 更新版本号

将 `pyneedle-pointer` 更新到 `0.2.1`。同时需要更新 `pyneedle-spec` 到 `0.1.5`。

~~~~~act
patch_file
packages/pyneedle-pointer/pyproject.toml
~~~~~
~~~~~toml.old
version = "0.2.0"
description = "Standard implementation of Semantic Pointers (L) for PyNeedle."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.3",
]
~~~~~
~~~~~toml.new
version = "0.2.1"
dependencies = [
    "pyneedle-spec ~= 0.1.5",
]
description = "Standard implementation of Semantic Pointers (L) for PyNeedle."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
~~~~~

~~~~~act
patch_file
packages/pyneedle-spec/pyproject.toml
~~~~~
~~~~~toml.old
version = "0.1.4"
~~~~~
~~~~~toml.new
version = "0.1.5"
~~~~~

~~~~~act
patch_file
packages/pyneedle/pyproject.toml
~~~~~
~~~~~toml.old
dependencies = [
    "pyneedle-spec ~= 0.1.4",
    "pyneedle-pointer ~= 0.2.0",
    "pyneedle-runtime ~= 0.1.4",
    "pyneedle-bus ~= 0.1.4",
]
~~~~~
~~~~~toml.new
dependencies = [
    "pyneedle-spec ~= 0.1.5",
    "pyneedle-pointer ~= 0.2.1",
    "pyneedle-runtime ~= 0.1.4",
    "pyneedle-bus ~= 0.1.4",
]
~~~~~

### 下一步建议
运行测试，确认无限迭代已被终结。之后，你将需要同步更新其他包（如 `runtime` 和 `bus`）的依赖版本（如果需要严格一致性），但由于这是一次向后兼容的修复，它们目前的宽容版本约束（`~= 0.1.4` 和 `~= 0.2.0`）理论上应该能接受新的 `spec` 和 `pointer`，只要它们安装时能解析到最新版。为了严谨，我们可以在下一个 Commit 计划中更新它们。
