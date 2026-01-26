好的，我理解了。你的分析完全正确，这是典型的“开发文档”与“用户文档”的分离，是保证项目清晰度的关键步骤。我们将执行这个重构。

`release_manager.py` 脚本的行为是正确的，因为它遵循了 `workspace.members` 的定义，而根目录不属于分发单元。

现在，我将生成一个计划来执行文档的重构。

## [WIP] refactor(docs): 为开发者和用户分离 README 文档

### 用户需求
1.  将根目录的 `README.md` 和 `README.zh.md` 移动到 `packages/pyneedle/` 目录下，作为面向 PyPI 用户的文档。
2.  修改 `packages/pyneedle/` 下的新 README 文件，更新安装说明（使用 `pip install pyneedle`），并移除不必要的架构和许可证部分。
3.  创建一个新的、简化的根 `README.md`，其内容面向开发者和贡献者。
4.  确保根 `README.md` 链接到 `packages/pyneedle/README.md`，以引导用户。
5.  更新 `packages/pyneedle/pyproject.toml` 以指定新的 `README.md` 路径。

### 评论
这是一个关键的架构改进，它在文档层面实现了“本体论正确性”。通过为开发者（在仓库根目录）和消费者（在 PyPI）提供专门定制的文档，我们消除了信息混淆，为两类受众都提供了更清晰、更专注的体验。

### 目标
1.  `packages/pyneedle` 包含一个完整的、适合在 PyPI 上展示的 `README.md`。
2.  根目录包含一个简洁的、面向开发者的 `README.md`，清晰地导航到用户文档。
3.  `pyneedle` 包的 `pyproject.toml` 正确配置，以便 PyPI 可以渲染其描述。

### 基本原理
我们将采用 `move_file` 来迁移现有的详细文档，这比重写更高效。然后，通过一系列精确的 `patch_file` 操作来移除对消费者不必要的部分并更新安装说明。最后，使用 `write_file` 来创建一个全新的、内容完全不同的根 `README.md`，因为它与旧版本的内容差异巨大。

### 标签
#intent/refine #intent/document #flow/ready #priority/medium #comp/docs #scope/dx #scope/ux #task/domain/devops #task/object/cd-pipeline #task/action/implementation #task/state/continue

---

### Script

#### Acts 1: 迁移 README 文件到 `pyneedle` 包

首先，我们将现有的详细 README 文件移动到它们作为“产品文档”的正确位置。

~~~~~act
move_file
README.md
packages/pyneedle/README.md
~~~~~

~~~~~act
move_file
README.zh.md
packages/pyneedle/README.zh.md
~~~~~

#### Acts 2: 更新 `pyneedle` 的 `pyproject.toml`

为了让 PyPI 能够找到并展示新的 README，我们必须在 `pyproject.toml` 中明确声明它。

~~~~~act
patch_file
packages/pyneedle/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle"
version = "0.1.1"
description = "Batteries-included distribution of the PyNeedle runtime."
authors = [
~~~~~
~~~~~toml.new
[project]
name = "pyneedle"
version = "0.1.1"
description = "Batteries-included distribution of the PyNeedle runtime."
readme = "README.md"
authors = [
~~~~~

#### Acts 3: 优化面向用户的 README (英文版)

现在，我们对 `pyneedle` 包内的 README 进行精简和修正，使其完全面向最终用户。

首先，移除对用户不必要的架构描述部分。

~~~~~act
patch_file
packages/pyneedle/README.md
~~~~~
~~~~~markdown.old
# Output: My App from File
```

## Architecture

PyNeedle is a monorepo composed of several focused packages:

-   `pyneedle-spec`: Defines the core `Protocol` interfaces for all components.
-   `pyneedle-pointer`: The standard implementation of `SemanticPointer` (`L`) and `PointerSet`.
-   `pyneedle-nexus`: The standard `OverlayNexus` runtime implementation and loaders like `MemoryLoader`.
-   `pyneedle-runtime`: Provides the `FileSystemLoader` and composes the other components into the batteries-included `needle` package.
-   `pyneedle`: The user-facing distribution that combines all of the above into a single, easy-to-use namespace package.
~~~~~
~~~~~markdown.new
# Output: My App from File
```
~~~~~

然后，更新安装说明，并移除许可证部分。

~~~~~act
patch_file
packages/pyneedle/README.md
~~~~~
~~~~~markdown.old
## Installation

Since this project is not yet available on PyPI, you need to install it from a local clone.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/doucx/stitcher-python.git
    cd stitcher-python
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # On Windows: .venv\Scripts\activate
    ```

3.  **Install the project in editable mode with development dependencies:**
    ```bash
    pip install -e .[dev]
    ```
    This will make the `needle` package and all its components available in your environment.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](./LICENSE) file for details.
~~~~~
~~~~~markdown.new
## Installation

Install the package from PyPI:
```bash
pip install pyneedle
```
~~~~~

#### Acts 4: 优化面向用户的 README (中文版)

对中文版的 README 执行同样的操作。

移除架构部分。

~~~~~act
patch_file
packages/pyneedle/README.zh.md
~~~~~
~~~~~markdown.old
# 输出: 从文件加载的应用
```

## 架构

PyNeedle 是一个由多个专注的包组成的 monorepo：

-   `pyneedle-spec`: 定义所有组件的核心 `Protocol` 接口。
-   `pyneedle-pointer`: `SemanticPointer` (`L`) 和 `PointerSet` 的标准实现。
-   `pyneedle-nexus`: 标准的 `OverlayNexus` 运行时实现和像 `MemoryLoader` 这样的加载器。
-   `pyneedle-runtime`: 提供 `FileSystemLoader` 并将其他组件组合成“开箱即用”的 `needle` 包。
-   `pyneedle`: 面向用户的发行版，将以上所有组件组合成一个单一、易于使用的命名空间包。
~~~~~
~~~~~markdown.new
# 输出: 从文件加载的应用
```
~~~~~

更新安装说明并移除许可证部分。

~~~~~act
patch_file
packages/pyneedle/README.zh.md
~~~~~
~~~~~markdown.old
## 安装

由于本项目尚未发布到 PyPI，您需要从本地克隆进行安装。

1.  **克隆仓库：**
    ```bash
    git clone https://github.com/doucx/stitcher-python.git
    cd stitcher-python
    ```

2.  **创建并激活虚拟环境：**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # 在 Windows 上: .venv\Scripts\activate
    ```

3.  **以可编辑模式安装项目及其开发依赖：**
    ```bash
    pip install -e .[dev]
    ```
    这将使 `needle` 包及其所有组件在您的环境中可用。

## 许可证

本项目采用 Apache License, Version 2.0 许可证。详情请参阅 [LICENSE](./LICENSE) 文件。
~~~~~
~~~~~markdown.new
## 安装

通过 PyPI 安装：
```bash
pip install pyneedle
```
~~~~~

#### Acts 5: 创建新的、面向开发者的根 README

最后，我们创建新的根 `README.md`，其内容专注于项目本身和贡献指南。

~~~~~act
write_file
README.md
~~~~~
~~~~~markdown
# PyNeedle Monorepo

![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)

This repository contains the source code for the PyNeedle ecosystem, a modern toolkit for decoupling meaning from implementation in Python applications.

---

## About this Repository

This is a monorepo managed with `uv` workspaces. It contains all the packages that make up the PyNeedle runtime.

**➡️ For user-facing documentation, quick start, and API examples, please see the `pyneedle` package [README](./packages/pyneedle/README.md).**

## Core Packages

-   `pyneedle-spec`: Defines the core `Protocol` interfaces for all components.
-   `pyneedle-pointer`: The standard implementation of `SemanticPointer` (`L`) and `PointerSet`.
-   `pyneedle-runtime`: Provides core operators like `FileSystemOperator` and composes other components.
-   `pyneedle`: The user-facing distribution that combines all of the above into a single, easy-to-use namespace package.

## Development Setup

To contribute to PyNeedle, you need to set up a local development environment.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/quipu-dev/Needle.git
    cd Needle
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # On Windows: .venv\Scripts\activate
    ```

3.  **Install all workspace packages and development dependencies:**
    ```bash
    pip install -e .[dev]
    ```
    This command installs all packages in editable mode and makes them available in your environment.

## Running Tests

To run the test suite, use `pytest`:
```bash
pytest
```

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](./LICENSE) file for details.
~~~~~

### 下一步建议
1.  **提交并验证**: 合并这些变更。新的 CD 流程会运行，但由于没有版本变化，它只会跳过所有包。
2.  **发布新版本**: 接下来，您可以为 `pyneedle` 包提升一个新的版本号（例如 `0.1.2`），然后合并到 `main`。这将触发一次真正的发布，您可以去 PyPI 验证 `pyneedle` 的页面是否已经正确显示了新的 README 内容。
