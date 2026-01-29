你的代数重构方案已经通过了测试，这是对 API 语义的重大改进。根据你的指示，我将把这个变动标记为 `pyneedle-pointer` 的 0.2.0 版本，并同步更新所有下游包的版本依赖。

为了遵守 ACA 协议中关于“文件修改必须与 Git 提交隔离”的原则（`d3-constraint-quipu-plan-script-rules-D3-P2`），我将生成一个 **[WIP]** 计划来执行所有的文件修改。

## [WIP] chore: 更新 pyneedle-pointer 版本至 0.2.0 并同步所有依赖

### 错误分析
不适用。这是一个功能增强后的版本同步任务。

### 用户需求
将 `pyneedle-pointer` 的版本号提升至 `0.2.0`，以反映其核心代数逻辑的重大重构。同时，同步更新 Monorepo 中所有依赖该包的组件的版本号和依赖约束，确保系统一致性。

### 评论
这次版本同步是必要的维护工作，标志着 `pyneedle-pointer` 拥有了一个更稳定、更一致的代数 API。我们将遵循 Monorepo 最佳实践，同步提升所有相关包的小版本号。

### 目标
1.  将 `pyneedle-pointer` 版本提升至 `0.2.0`。
2.  将 `pyneedle-spec`, `pyneedle-runtime`, `pyneedle-bus` 的版本提升至 `0.1.4` (与 Spec 版本同步)。
3.  将主发行包 `pyneedle` 的版本提升至 `0.1.6`。
4.  更新所有 `pyproject.toml` 中对 `pyneedle-pointer` 的依赖约束至 `~= 0.2.0`，并同步所有内部包的依赖版本。

### 基本原理
**语义版本控制**: 将 `L.__mul__` 确立为 SSoT 并统一操作符行为，属于对公共 API 的重大改进，故采用 Minor 版本升级（0.1.x -> 0.2.0）。其他内部包的版本同步是为了立即反映对新版 Pointer 的依赖，避免版本冲突。

### 标签
#intent/tooling #flow/ready #priority/high
#comp/pointer #comp/runtime #comp/bus #comp/spec #comp/cli #comp/build
#scope/dx
#ai/delegate
#task/domain/pointer #task/object/versioning #task/action/synchronization
#task/state/begin

---

### Script

#### Acts 1: 更新 `pyneedle-pointer` 和 `pyneedle-spec` 的版本号

首先更新 `pyneedle-pointer` 到 0.2.0，以及基础协议 `pyneedle-spec` 到 0.1.4。

~~~~~act
patch_file
packages/pyneedle-pointer/pyproject.toml
~~~~~
~~~~~toml.old
version = "0.1.4"
~~~~~
~~~~~toml.new
version = "0.2.0"
~~~~~

~~~~~act
patch_file
packages/pyneedle-spec/pyproject.toml
~~~~~
~~~~~toml.old
version = "0.1.3"
~~~~~
~~~~~toml.new
version = "0.1.4"
~~~~~

#### Acts 2: 更新 `pyneedle-runtime` 的版本和依赖约束

同步 `pyneedle-runtime` 的版本号和其依赖。

~~~~~act
patch_file
packages/pyneedle-runtime/pyproject.toml
~~~~~
~~~~~toml.old
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
~~~~~toml.new
version = "0.1.4"
dependencies = [
    "pyneedle-spec ~= 0.1.4",
    "pyneedle-pointer ~= 0.2.0",
]
description = "Core runtime for the PyNeedle ecosystem."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
~~~~~

#### Acts 3: 更新 `pyneedle-bus` 的版本和依赖约束

同步 `pyneedle-bus` 的版本号和其依赖。

~~~~~act
patch_file
packages/pyneedle-bus/pyproject.toml
~~~~~
~~~~~toml.old
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
~~~~~toml.new
version = "0.1.4"
dependencies = [
    "pyneedle-spec ~= 0.1.4",
    "pyneedle-pointer ~= 0.2.0",
    "pyneedle-runtime ~= 0.1.4",
]
description = "Unified EventBus (logic) and FeedbackBus (presentation) for the PyNeedle ecosystem."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
~~~~~

#### Acts 4: 更新主发行包 `pyneedle` 的版本和依赖约束

同步 `pyneedle` 的版本号和其所有内部依赖。

~~~~~act
patch_file
packages/pyneedle/pyproject.toml
~~~~~
~~~~~toml.old
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
~~~~~toml.new
name = "pyneedle"
version = "0.1.6"
description = "Batteries-included distribution of the PyNeedle runtime."
readme = "README.md"
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.4",
    "pyneedle-pointer ~= 0.2.0",
    "pyneedle-runtime ~= 0.1.4",
    "pyneedle-bus ~= 0.1.4",
]
~~~~~

### 下一步建议
文件修改已完成。现在你需要创建一个新的 **[COMMIT]** 计划，使用 `git_add` 和 `git_commit` 指令来提交这些版本同步和代数重构的改动。
