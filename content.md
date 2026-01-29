## fix: 修复由于 Protocol 无法进行运行时检查导致的测试失败。

### 错误分析

错误原因非常明确：在 `PointerSet._broadcast` 中，我们使用了 `isinstance(res, SemanticPointerProtocol)` 来判断结果是否为原子指针。但在 Python 中，除非使用 `@typing.runtime_checkable` 装饰器，否则 `Protocol` 类型不能用于 `isinstance` 检查。

这暴露了 `pyneedle-spec` 的一个设计疏忽。作为一个旨在提供“高性能、互操作”能力的系统，所有的核心协议都应当支持运行时检查。

### 用户需求
修复由于 Protocol 无法进行运行时检查导致的测试失败。

### 目标
1.  修改 `packages/pyneedle-spec/src/needle/spec/protocols.py`，为所有核心协议添加 `@runtime_checkable`。
2.  更新 `pyneedle-spec` 的版本号至 `0.1.3`。

### 基本原理
根据 **HFEA v1.0** 的“基础设施优先”原则，当底层 Spec 无法支撑上层架构进化时，必须优先修复 Spec。增加 `@runtime_checkable` 是让 `PointerSet` 的单子（Monadic）广播引擎能够正常工作的唯一“正规军”做法。

### 标签
#intent/fix #flow/ready #priority/critical
#comp/spec #scope/core
#ai/instruct
#task/domain/spec #task/object/protocols #task/action/fix
#task/state/continue #task/status/active

---

### Script

#### Acts 1: 升级底层协议为可运行时检查

我们将修改 `packages/pyneedle-spec/src/needle/spec/protocols.py`。

~~~~~act
patch_file
packages/pyneedle-spec/src/needle/spec/protocols.py
~~~~~
~~~~~python.old
from typing import Protocol, Any, Union, Iterable, TypeVar

# T_co is covariant, meaning SemanticPointerProtocol can return subtypes of itself
T_Pointer = TypeVar("T_Pointer", bound="SemanticPointerProtocol", covariant=True)


class SemanticPointerProtocol(Protocol[T_Pointer]):
~~~~~
~~~~~python.new
from typing import Protocol, Any, Union, Iterable, TypeVar, runtime_checkable

# T_co is covariant, meaning SemanticPointerProtocol can return subtypes of itself
T_Pointer = TypeVar("T_Pointer", bound="SemanticPointerProtocol", covariant=True)


@runtime_checkable
class SemanticPointerProtocol(Protocol[T_Pointer]):
~~~~~
~~~~~act
patch_file
packages/pyneedle-spec/src/needle/spec/protocols.py
~~~~~
~~~~~python.old
class PointerSetProtocol(Protocol):
    def __iter__(self) -> Iterable[SemanticPointerProtocol]: ...
~~~~~
~~~~~python.new
@runtime_checkable
class PointerSetProtocol(Protocol):
    def __iter__(self) -> Iterable[SemanticPointerProtocol]: ...
~~~~~
~~~~~act
patch_file
packages/pyneedle-spec/src/needle/spec/protocols.py
~~~~~
~~~~~python.old
class OperatorProtocol(Protocol):
    def __call__(self, key: Any) -> Any: ...


class RendererProtocol(Protocol):
    def render(self, message: str, level: str = "info", **kwargs: Any) -> None: ...
~~~~~
~~~~~python.new
@runtime_checkable
class OperatorProtocol(Protocol):
    def __call__(self, key: Any) -> Any: ...


@runtime_checkable
class RendererProtocol(Protocol):
    def render(self, message: str, level: str = "info", **kwargs: Any) -> None: ...
~~~~~

#### Acts 2: 更新 pyneedle-spec 版本号

~~~~~act
patch_file
packages/pyneedle-spec/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-spec"
version = "0.1.2"
description = "Core protocols and specifications for the PyNeedle ecosystem."
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-spec"
version = "0.1.3"
description = "Core protocols and specifications for the PyNeedle ecosystem."
~~~~~

### 下一步建议
- **重新执行测试**: 修复底层协议后，再次运行 `pytest packages/pyneedle-pointer/tests/test_pointer_algebra.py`。
- **架构审查**: 此时 `PointerSet` 的展平逻辑应该能够正确识别原子指针并正常工作。
