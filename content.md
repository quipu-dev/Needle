基于我们对 `pyneedle-pointer` 实现的增强，**确实需要更新 `pyneedle-spec`**。

协议（Protocols）是整个系统的契约。如果协议不更新，类型检查工具（如 Pyright 或 Mypy）在处理 `L['a', 'b']` 时会报错，因为它认为 `__getitem__` 只接受 `str/int` 且必须返回单个指针。

以下是具体的分析和更新建议：

### 1. `SemanticPointerProtocol` 的变更
*   **输入类型**: 必须从 `Union[str, int]` 放宽到 `Any`，以支持 `tuple`（多重索引）。
*   **返回类型**: 必须从 `T_Pointer` 变为 `Union[T_Pointer, "PointerSetProtocol"]`。这是最重要的变化，体现了索引操作的“多态性”。

### 2. `PointerSetProtocol` 的变更
*   **广播支持**: 需要显式定义 `__getattr__` 和 `__getitem__`，以支持属性广播和索引广播。
*   **返回类型一致性**: 确保所有广播操作都返回 `PointerSetProtocol`。

---

## [WIP] refactor(spec): 同步指针协议以支持多态索引与广播

### 用户需求
更新 `pyneedle-spec` 以匹配 `pyneedle-pointer` 的新能力，确保类型系统能够正确理解多重索引和集合广播。

### 评论
协议是系统的“法律”。如果我们改变了实现但没有更新协议，那么对于使用该库的开发者来说，新功能在 IDE 中将是“不可见”的或显示为类型错误。

### 目标
1. 更新 `packages/pyneedle-spec/src/needle/spec/protocols.py`。
2. 提升 `pyneedle-spec` 的版本号至 `0.1.2`。

### 标签
#intent/architect #flow/ready #priority/high
#comp/spec #concept/navigation #scope/api
#ai/instruct
#task/domain/spec #task/object/protocols #task/action/refactor
#task/state/continue

---

### Script

#### Acts 1: 更新协议定义

我们将修改 `protocols.py`，使契约能够描述新的行为。

~~~~~act
patch_file
packages/pyneedle-spec/src/needle/spec/protocols.py
~~~~~
~~~~~python.old
class SemanticPointerProtocol(Protocol[T_Pointer]):
    def __getattr__(self, name: str) -> T_Pointer: ...

    def __str__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __eq__(self, other: Any) -> bool: ...

    def __add__(self, other: Any) -> T_Pointer: ...

    def __truediv__(
        self, other: Union[str, "SemanticPointerProtocol"]
    ) -> T_Pointer: ...

    def __mul__(self, other: Any) -> "PointerSetProtocol": ...


class PointerSetProtocol(Protocol):
    def __iter__(self) -> Iterable[SemanticPointerProtocol]: ...

    def __truediv__(
        self, other: Union[str, SemanticPointerProtocol]
    ) -> "PointerSetProtocol": ...

    def __or__(self, other: "PointerSetProtocol") -> "PointerSetProtocol": ...

    def __add__(
        self, other: Union[str, SemanticPointerProtocol]
    ) -> "PointerSetProtocol": ...

    def __mul__(self, other: Any) -> "PointerSetProtocol": ...
~~~~~
~~~~~python.new
class SemanticPointerProtocol(Protocol[T_Pointer]):
    def __getattr__(self, name: str) -> T_Pointer: ...

    def __str__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __eq__(self, other: Any) -> bool: ...

    def __add__(self, other: Any) -> T_Pointer: ...

    def __truediv__(
        self, other: Union[str, "SemanticPointerProtocol"]
    ) -> T_Pointer: ...

    def __mul__(self, other: Any) -> "PointerSetProtocol": ...

    def __getitem__(self, key: Any) -> Union[T_Pointer, "PointerSetProtocol"]: ...


class PointerSetProtocol(Protocol):
    def __iter__(self) -> Iterable[SemanticPointerProtocol]: ...

    def __getattr__(self, name: str) -> "PointerSetProtocol": ...

    def __getitem__(self, key: Any) -> "PointerSetProtocol": ...

    def __truediv__(
        self, other: Union[str, SemanticPointerProtocol]
    ) -> "PointerSetProtocol": ...

    def __or__(self, other: "PointerSetProtocol") -> "PointerSetProtocol": ...

    def __add__(
        self, other: Union[str, SemanticPointerProtocol]
    ) -> "PointerSetProtocol": ...

    def __mul__(self, other: Any) -> "PointerSetProtocol": ...
~~~~~

#### Acts 2: 提升 pyneedle-spec 版本号

~~~~~act
patch_file
packages/pyneedle-spec/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-spec"
version = "0.1.1"
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-spec"
version = "0.1.2"
~~~~~

### 下一步建议
- **同步主包版本**: 由于核心 API 发生了显著变化（增加了多重索引和广播），建议将 `pyneedle` (meta-package) 以及 `pyneedle-pointer` 的版本也同步提升，并更新它们对 `pyneedle-spec` 的依赖版本要求。
- **发布准备**: 如果这些改动已经过测试验证，可以准备进行一次 Git Commit。
