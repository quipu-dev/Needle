好的，我们开始实施激进的统一策略。首先在 `Needle` 仓库中构建 `pyneedle-bus` 的骨架，并将其集成到工作区配置中。

我将生成一个计划来执行这些操作。

## [WIP] feat: 创建 pyneedle-bus 包骨架并集成到工作区

### 用户需求

根据架构统一计划，需要在 `Needle` 仓库中创建一个新的 `pyneedle-bus` 包。这包括：
1.  创建标准的包目录结构和 `__init__.py` 文件。
2.  为其编写 `pyproject.toml` 配置文件，声明其元数据和依赖项。
3.  更新根 `pyproject.toml` 以将新包纳入开发和测试环境。
4.  更新 `pyneedle` 元包以依赖这个新的 bus 包。

### 评论

这是“中心突破，边缘绞杀”策略的第一步，也是最关键的一步。通过在 `Needle` 仓库中建立一个功能完备、配置正确的 `pyneedle-bus` 包，我们为后续从 `Stitcher`、`Quipu` 和 `Cascade` 中移除旧 bus 实现并转向统一依赖奠定了坚实的基础。此举将立即统一整个项目的构建、测试和类型检查路径。

### 目标

1.  在 `packages/` 目录下成功创建 `pyneedle-bus` 的完整目录结构。
2.  为 `pyneedle-bus` 创建一个符合规范的 `pyproject.toml`，使其依赖于 `pyneedle-spec` 和 `pyneedle-pointer`。
3.  确保根 `pyproject.toml` 正确配置，以便 `uv`、`pytest` 和 `pyright` 能够识别并处理新包。
4.  确保 `pyneedle` 元包将 `pyneedle-bus` 作为其核心依赖之一。

### 基本原理

我们将采用原子化的步骤来完成此任务。首先，使用 `run_command` 快速创建目录结构。接着，使用 `write_file` 创建新包的配置文件和初始化文件。最后，通过 `patch_file` 对现有配置文件进行精确的、上下文感知的修改，以避免破坏现有结构。这种方法确保了操作的幂等性和可追溯性。

### 标签

#intent/build #flow/ready #priority/high #comp/build #concept/dependency #scope/dx #task/domain/bus #task/object/package-skeleton #task/action/implementation #task/state/begin

---

### Script

#### Acts 1: 创建目录结构

首先，我们为新包创建标准的目录结构。

~~~~~act
run_command
~~~~~
~~~~~
mkdir -p packages/pyneedle-bus/src/needle/bus
~~~~~

#### Acts 2: 创建 `__init__.py` 文件

现在，我们创建必要的 `__init__.py` 文件，确保 `needle` 作为一个命名空间包可以被正确识别。

~~~~~act
write_file
packages/pyneedle-bus/src/needle/__init__.py
~~~~~
~~~~~python
# This allows this package to coexist with other distribution packages
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
~~~~~

~~~~~act
write_file
packages/pyneedle-bus/src/needle/bus/__init__.py
~~~~~
~~~~~python
# pyneedle-bus: Unified EventBus (logic) and FeedbackBus (presentation)
~~~~~

#### Acts 3: 创建 `pyproject.toml`

为 `pyneedle-bus` 创建 `pyproject.toml`，定义其元数据和依赖关系。

~~~~~act
write_file
packages/pyneedle-bus/pyproject.toml
~~~~~
~~~~~toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "pyneedle-bus"
version = "0.1.0"
description = "Unified EventBus (logic) and FeedbackBus (presentation) for the PyNeedle ecosystem."
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec ~= 0.1.0",
    "pyneedle-pointer ~= 0.1.0",
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Typing :: Typed",
]
keywords = ["semantic", "pointer", "needle", "bus", "event", "feedback", "i18n"]

[project.urls]
Homepage = "https://github.com/quipu-dev/Needle"
Repository = "https://github.com/quipu-dev/Needle"
"Bug Tracker" = "https://github.com/quipu-dev/Needle/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/needle"]

[tool.uv.sources]
pyneedle-spec = { workspace = true }
pyneedle-pointer = { workspace = true }
~~~~~

#### Acts 4: 更新根 `pyproject.toml`

将新包集成到整个 monorepo 的开发环境中。

~~~~~act
patch_file
pyproject.toml
~~~~~
~~~~~toml
[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "ruff",
    "mypy",
    "pyneedle",
    "pyneedle-pointer",
    "pyneedle-runtime",
    "pyneedle-spec",
]
~~~~~
~~~~~toml
[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "ruff",
    "mypy",
    "pyneedle",
    "pyneedle-bus",
    "pyneedle-pointer",
    "pyneedle-runtime",
    "pyneedle-spec",
]
~~~~~

~~~~~act
patch_file
pyproject.toml
~~~~~
~~~~~toml
[tool.uv.sources]
pyneedle = { workspace = true }
pyneedle-runtime = { workspace = true }
pyneedle-pointer = { workspace = true }
pyneedle-spec = { workspace = true }
~~~~~
~~~~~toml
[tool.uv.sources]
pyneedle = { workspace = true }
pyneedle-bus = { workspace = true }
pyneedle-runtime = { workspace = true }
pyneedle-pointer = { workspace = true }
pyneedle-spec = { workspace = true }
~~~~~

~~~~~act
patch_file
pyproject.toml
~~~~~
~~~~~toml
pythonpath = [
    "packages/pyneedle/src",
    "packages/pyneedle-pointer/src",
    "packages/pyneedle-runtime/src",
    "packages/pyneedle-spec/src",
]
~~~~~
~~~~~toml
pythonpath = [
    "packages/pyneedle/src",
    "packages/pyneedle-bus/src",
    "packages/pyneedle-pointer/src",
    "packages/pyneedle-runtime/src",
    "packages/pyneedle-spec/src",
]
~~~~~

~~~~~act
patch_file
pyproject.toml
~~~~~
~~~~~toml
extraPaths = [
    "packages/pyneedle-spec/src",
    "packages/pyneedle-pointer/src",
    "packages/pyneedle-runtime/src",
    "packages/pyneedle/src",
    "packages/needle-stubs/src",
]
~~~~~
~~~~~toml
extraPaths = [
    "packages/pyneedle-spec/src",
    "packages/pyneedle-bus/src",
    "packages/pyneedle-pointer/src",
    "packages/pyneedle-runtime/src",
    "packages/pyneedle/src",
    "packages/needle-stubs/src",
]
~~~~~

#### Acts 5: 更新 `pyneedle` 元包

最后，我们将 `pyneedle-bus` 添加到 `pyneedle` 元包的依赖中，使其成为核心组件。

~~~~~act
patch_file
packages/pyneedle/pyproject.toml
~~~~~
~~~~~toml
dependencies = [
    "pyneedle-spec ~= 0.1.0",
    "pyneedle-pointer ~= 0.1.0",
    "pyneedle-runtime ~= 0.1.0",
]
~~~~~
~~~~~toml
dependencies = [
    "pyneedle-spec ~= 0.1.0",
    "pyneedle-pointer ~= 0.1.0",
    "pyneedle-runtime ~= 0.1.0",
    "pyneedle-bus ~= 0.1.0",
]
~~~~~

~~~~~act
patch_file
packages/pyneedle/pyproject.toml
~~~~~
~~~~~toml
[tool.uv.sources]
pyneedle-spec = { workspace = true }
pyneedle-pointer = { workspace = true }
pyneedle-runtime = { workspace = true }
~~~~~
~~~~~toml
[tool.uv.sources]
pyneedle-spec = { workspace = true }
pyneedle-pointer = { workspace = true }
pyneedle-runtime = { workspace = true }
pyneedle-bus = { workspace = true }
~~~~~

### 下一步建议

骨架已经搭建完毕。接下来的关键任务是填充 `pyneedle-bus` 的内容：
1.  **实现 `EventBus`**: 从 `cascade.bus.core` 移植核心逻辑，并增强对 `SemanticPointer` 的支持。
2.  **实现 `FeedbackBus`**: 从 `stitcher.bus` 移植渲染逻辑和 `operator` 注入机制。
3.  **实现 `MessageStore`**: 从 `cascade.bus.messages` 移植加载逻辑，并实现多资源根的注册机制。

一旦这些核心组件就位，我们就可以开始对 `Stitcher` 进行第一个“心脏移植”手术。
