我们已经完成了指针代数的核心增强。为了保持 Monorepo 内各组件的一致性并反映这一重大的 API 变更，现在需要同步提升所有相关包的版本号，并更新它们之间的依赖约束。

## [WIP] chore(version): 提升所有相关包的版本号并同步依赖约束

### 用户需求
同步提升整个 `PyNeedle` 生态系统的版本号，确保所有组件都依赖于包含“多重索引和广播”能力的新版协议和实现。

### 评论
在 Monorepo 模式下，当核心协议（Spec）发生破坏性或重大功能性变更时，同步提升子包版本是最佳实践。这可以防止在不同版本混合使用时出现令人困惑的类型错误。

### 目标
1. 将 `pyneedle-spec`, `pyneedle-pointer`, `pyneedle-bus`, `pyneedle-runtime` 同步提升至 `0.1.2`。
2. 将元包 `pyneedle` 提升至 `0.1.4`。
3. 更新所有 `pyproject.toml` 中的交叉依赖，指向 `~= 0.1.2`。

### 基本原理
通过统一提升到 `0.1.2`，我们确立了一个新的“功能基线”。依赖项使用 `~= 0.1.2` 约束，既保证了向前兼容性，又强制要求安装包含最新特性的版本。

### 标签
#intent/tooling #flow/ready #priority/medium
#comp/build #scope/dx
#ai/instruct
#task/domain/build #task/object/versioning #task/action/refactor
#task/state/continue

---

### Script

#### Acts 1: 更新各子包版本及依赖

我们将逐个修改 `pyproject.toml` 文件。

~~~~~act
patch_file
packages/pyneedle-pointer/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-pointer"
version = "0.1.1"
description = "Standard implementation of Semantic Pointers (L) for PyNeedle."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.0",
]
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-pointer"
version = "0.1.2"
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

~~~~~act
patch_file
packages/pyneedle-bus/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-bus"
version = "0.1.1"
description = "Unified EventBus (logic) and FeedbackBus (presentation) for the PyNeedle ecosystem."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.1",
    "pyneedle-pointer ~= 0.1.0",
    "pyneedle-runtime ~= 0.1.0",
]
~~~~~
~~~~~toml.new
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

~~~~~act
patch_file
packages/pyneedle-runtime/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-runtime"
version = "0.1.1"
description = "Core runtime for the PyNeedle ecosystem."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.0",
    "pyneedle-pointer ~= 0.1.0",
]
~~~~~
~~~~~toml.new
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

#### Acts 2: 更新元包 pyneedle 版本

~~~~~act
patch_file
packages/pyneedle/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle"
version = "0.1.3"
description = "Batteries-included distribution of the PyNeedle runtime."
readme = "README.md"
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.0",
    "pyneedle-pointer ~= 0.1.0",
    "pyneedle-runtime ~= 0.1.0",
    "pyneedle-bus ~= 0.1.0",
]
~~~~~
~~~~~toml.new
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

### 下一步建议
- **提交代码**: 核心代数逻辑和版本更新已就绪，可以进行 Git 提交。
- **重构总线逻辑**: 版本同步完成后，我们可以正式开始实现 `pyneedle-bus` 的 MQTT 通配符匹配功能。
