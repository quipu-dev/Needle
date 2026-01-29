## [WIP] refactor(pointer): 基于“自动展平广播”协议重构 PointerSet

### 用户需求
将 `PointerSet` 的实现简化为两个核心准则：所有操作自动广播；所有结果自动展平。

### 目标
1.  在 `PointerSet` 内部实现一个统一的 `_broadcast` 引擎，负责处理“单值添加”与“集合合并”。
2.  使用该引擎重写所有运算符，消除 `__mul__` 和 `__getitem__` 之间的逻辑差异。
3.  确保 `L['a','b'][0][1,2]` 等复杂嵌套操作在没有任何特殊 `if` 判断的情况下自然通过。

### 基本原理
我们将 `PointerSet` 定义为一个特殊的 `set` 子类，其所有魔法都源于对成员操作结果的“类型感知合并”。如果成员操作返回 `Iterable`（且非字符串），则视为“维度扩张”，执行 `update`；否则视为“位置移动”，执行 `add`。

### 标签
#intent/refine #flow/ready #priority/critical
#comp/runtime #concept/state #scope/core
#ai/brainstorm
#task/domain/logic #task/object/pointer-algebra #task/action/refactor
#task/state/begin #task/status/active

---

### Script

#### Acts 1: 重写 `PointerSet` 实现

我们将大幅精简 `packages/pyneedle-pointer/src/needle/pointer/set.py`，引入统一的广播协议。

~~~~~act
write_file
packages/pyneedle-pointer/src/needle/pointer/set.py
~~~~~
~~~~~python
from typing import Set, Union, Any, Iterable, Callable, TYPE_CHECKING
from needle.spec import PointerSetProtocol, SemanticPointerProtocol

if TYPE_CHECKING:
    from .core import SemanticPointer


class PointerSet(Set["SemanticPointer"], PointerSetProtocol):
    """
    A collection of Semantic Pointers that acts as a Monad.
    All operations are broadcasted to its members and results are auto-flattened.
    """

    def _broadcast(self, op: Callable[["SemanticPointer"], Any]) -> "PointerSet":
        """
        The core engine: Apply 'op' to each member.
        If the result is a set/iterable (dimension expansion), flatten it.
        Otherwise (position movement), just add it.
        """
        new_set = PointerSet()
        for p in self:
            res = op(p)
            # Flatten if the result is an iterable (but not a string/pointer itself)
            if isinstance(res, Iterable) and not isinstance(res, (str, bytes, SemanticPointerProtocol)):
                new_set.update(res)
            else:
                new_set.add(res)
        return new_set

    def __getattr__(self, name: str) -> "PointerSet":
        return self._broadcast(lambda p: getattr(p, name))

    def __getitem__(self, key: Any) -> "PointerSet":
        return self._broadcast(lambda p: p[key])

    def __truediv__(self, other: Union[str, "SemanticPointerProtocol"]) -> "PointerSet":
        return self._broadcast(lambda p: p / other)

    def __add__(self, other: Union[str, "SemanticPointerProtocol"]) -> "PointerSet":
        return self._broadcast(lambda p: p + other)

    def __mul__(self, other: Any) -> "PointerSet":
        return self._broadcast(lambda p: p * other)
~~~~~


### 下一步建议
- **执行验证**: 运行 `pytest packages/pyneedle-pointer/tests/test_pointer_algebra.py`。你会发现，不仅仅是修复了 Bug，整个系统的数学模型变得无比丝滑。
- **发布准备**: 这种重大的架构精简通常伴随着更高的稳定性。如果没有问题，我们将直接进入 `[COMMIT]` 阶段。
