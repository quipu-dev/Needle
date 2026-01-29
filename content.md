好的，这是一次全系统的版本同步。由于 `pyneedle-spec` 引入了 `@runtime_checkable` 这一关键基础设施变更，且 `pyneedle-pointer` 实现了“单子化广播”重构，我们需要确保所有下游包不仅提升自身版本，还要更新它们的依赖声明以锁定这些新特性。

根据你的要求，版本号演进如下：
- `pyneedle-spec`: `0.1.3` (保持)
- `pyneedle-pointer`: `0.1.3` -> `0.1.4`
- `pyneedle-runtime`: `0.1.2` -> `0.1.3`
- `pyneedle-bus`: `0.1.2` -> `0.1.3`
- `pyneedle`: `0.1.4` -> `0.1.5`

## [WIP] chore: 同步更新所有包版本号与依赖约束以适配 Spec 0.1.3

### 用户需求
在 `pyneedle-spec` 和 `pyneedle-pointer` 发生重大重构后，同步提升 Monorepo 中所有受影响包的版本号，并更新其内部依赖关系。

### 评论
这是一次全系统的“对齐”操作。确保所有组件都指向支持运行时检查（Runtime Checkable）的协议版本，是系统在大规模重构后保持稳定的关键。

### 目标
1.  提升 `pyneedle-pointer`, `pyneedle-runtime`, `pyneedle-bus` 和 `pyneedle` 的版本号。
2.  更新各包 `pyproject.toml` 中的 `dependencies` 列表，确保它们依赖于最新的 spec 和相关组件版本。

### 基本原理
当底层协议（Spec）发生破坏性或重要功能增强（如增加 `@runtime_checkable`）时，所有直接或间接依赖该协议的包都应同步发布新版本。这有助于包管理器（如 uv 或 pip）在复杂的依赖树中正确解析出兼容的组件组合。

### 标签
#intent/tune #flow/ready #priority/medium
#comp/build #scope/dx
#ai/instruct
#task/domain/build #task/object/versioning #task/action/sync
#task/state/continue #task/status/active

---

### Script

#### Acts 1: 更新 pyneedle-pointer

提升版本号并同步 spec 依赖。

~~~~~act
patch_file
packages/pyneedle-pointer/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-pointer"
version = "0.1.3"
description = "Standard implementation of Semantic Pointers (L) for PyNeedle."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.2",
]
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-pointer"
version = "0.1.4"
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

#### Acts 2: 更新 pyneedle-runtime

提升版本号并同步 spec 与 pointer 依赖。

~~~~~act
patch_file
packages/pyneedle-runtime/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-runtime"
version = "0.1.2"
description = "Core runtime for the PyNeedle ecosystem."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.2",
    "pyneedle-pointer ~= 0.1.2",
]
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-runtime"
version = "0.1.3"
description = "Core runtime for the PyNeedle ecosystem."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.3",
    "pyneedle-pointer ~= 0.1.4",
]
~~~~~

#### Acts 3: 更新 pyneedle-bus

提升版本号并同步下游依赖。

~~~~~act
patch_file
packages/pyneedle-bus/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-bus"
version = "0.1.2"
description = "Unified EventBus (logic) and FeedbackBus (presentation) for the PyNeedle ecosystem."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.2",
    "pyneedle-pointer ~= 0.1.2",
    "pyneedle-runtime ~= 0.1.2",
]
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-bus"
version = "0.1.3"
description = "Unified EventBus (logic) and FeedbackBus (presentation) for the PyNeedle ecosystem."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.3",
    "pyneedle-pointer ~= 0.1.4",
    "pyneedle-runtime ~= 0.1.3",
]
~~~~~

#### Acts 4: 更新总发行版 pyneedle

作为“电池内置”的分发版，它必须反映所有子组件的最新状态。

~~~~~act
patch_file
packages/pyneedle/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle"
version = "0.1.4"
description = "Batteries-included distribution of the PyNeedle runtime."
readme = "README.md"
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.2",
    "pyneedle-pointer ~= 0.1.2",
    "pyneedle-runtime ~= 0.1.2",
    "pyneedle-bus ~= 0.1.2",
]
~~~~~
~~~~~toml.new
[project]
name = "pyneedle"
version = "0.1.5"
description = "Batteries-included distribution of the PyNeedle runtime."
readme = "README.md"
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.3",
    "pyneedle-pointer ~= 0.1.4",
    "pyneedle-runtime ~= 0.1.3",
    "pyneedle-bus ~= 0.1.3",
]
~~~~~

### 下一步建议
- **同步环境**: 建议运行 `uv sync` 以确保本地虚拟环境加载了最新的版本定义。
- **提交变更**: 完成版本同步后，我们将进行最终的提交。这将是一个标记系统进入“Monadic 时代”的重要里程碑。
