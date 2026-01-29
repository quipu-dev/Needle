收到指令，我将创建一个 **[COMMIT]** 计划，提交所有关于 `SemanticPointer` 代数重构和版本同步的修改。

## [COMMIT] refactor: Unify SemanticPointer algebra via __mul__

### 错误分析
不适用。

### 用户需求
提交所有关于 `pyneedle-pointer` 代数重构（统一操作符至 `__mul__`）和版本号同步的修改。

### 评论
这次提交包含了一次重要的架构重构和相应的版本升级。通过将 `__getitem__`, `__truediv__`, `__add__` 等操作统一委托给 `__mul__`，我们确立了一个清晰的代数 SSoT。这解决了用户在使用列表或集合进行路径拼接时出现的行为不一致性（例如 `L / [1,2]`）。同时，递归展平确保了多维度的集合操作始终返回扁平化的 `PointerSet`。

### 目标
提交以下文件：
1.  `pyneedle-pointer/src/needle/pointer/core.py`
2.  `pyneedle-pointer/tests/test_pointer_algebra.py`
3.  所有 `pyproject.toml` 文件中关于版本号的更新。

### 基本原理
**代数 SSoT**: 统一代数操作确保了 `L * keys`, `L[keys]`, `L / keys` 在 `keys` 为集合时具有相同的集合扩展语义，从而消除 API 歧义。
**版本同步**: `pyneedle-pointer` 升级至 0.2.0，所有依赖包同步升级版本号，以反映对新版核心库的依赖。

### 标签
#intent/refine #flow/ready #priority/high
#comp/pointer #comp/build #scope/api #scope/dx #concept/algebra
#ai/delegate
#task/domain/pointer #task/object/semantic-pointer #task/action/refactor
#task/state/end #task/status/completed

---

### Script

#### Acts 1: 暂存所有修改的文件

将所有被修改的文件（包括逻辑文件、测试文件和配置清单）添加到 Git 暂存区。

~~~~~act
git_add
packages/pyneedle-pointer/src/needle/pointer/core.py
packages/pyneedle-pointer/tests/test_pointer_algebra.py
packages/pyneedle-pointer/pyproject.toml
packages/pyneedle-spec/pyproject.toml
packages/pyneedle-runtime/pyproject.toml
packages/pyneedle-bus/pyproject.toml
packages/pyneedle/pyproject.toml
~~~~~

#### Acts 2: 创建 Git 提交

创建包含详细描述的 Git 提交。

~~~~~act
git_commit
~~~~~
~~~~~text
refactor(pointer): Unify SemanticPointer algebra via __mul__

This commit fundamentally refactors the SemanticPointer's algebraic operations to ensure semantic consistency across all composition operators.

The core logic for path concatenation vs. set expansion has been consolidated into `__mul__` (multiplication/distribution).

Key Changes:

1.  **SSoT for Composition**: `__getitem__`, `__truediv__ (/), and `__add__ (+)` are now aliases for `__mul__ (*)`.
2.  **Behavioral Polymorphism**: The type of input determines the output type:
    *   Atomic input (str, L): Returns a single `SemanticPointer`.
    *   Container input (list, tuple, set): Recursively flattens the container and returns a `PointerSet`.
3.  **Recursive Flattening**: Nested containers (e.g., `L[[[1, 2]]]`) are correctly flattened, ensuring that the final PointerSet contains only atomic pointers (`{L.1, L.2}`).

chore: Bump versions to reflect breaking API change in pointer core.
*   pyneedle-pointer: 0.1.4 -> 0.2.0
*   pyneedle-spec: 0.1.3 -> 0.1.4
*   pyneedle-runtime: 0.1.3 -> 0.1.4
*   pyneedle-bus: 0.1.3 -> 0.1.4
*   pyneedle: 0.1.5 -> 0.1.6
~~~~~

### 下一步建议
代数重构和版本同步任务已完成并提交。你现在可以继续下一个开发任务，例如集成和使用新的、更健壮的代数 API。
