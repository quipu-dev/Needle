好的，这是一个非常合理的请求，旨在提升项目的开发者体验（DX）。一个配置完善的根 `pyproject.toml` 是 monorepo 项目易用性的关键。

经过分析，我发现除了你提到的两点，`pytest` 的 `pythonpath` 配置也缺少了 `pyneedle` 包的路径，这会在运行测试时导致潜在的导入问题。

我将生成一个计划来一次性修复这些问题。

## [WIP] chore: 完善项目根依赖配置与测试路径

### 用户需求
1.  将 `pyneedle` 等核心包添加到根目录 `pyproject.toml` 的 `dependencies` 中，以便通过 `pip install .` 直接安装。
2.  在两个地方的依赖列表中添加 `pyneedle-runtime`。
3.  检查并修复其他可能存在的配置缺失问题。

### 评论
这是一个关键的开发者体验改进。通过在根 `pyproject.toml` 中定义核心依赖，我们为新加入的开发者提供了一个单一、明确的入口点来设置环境。同时，补全 `pytest` 的 `pythonpath` 遵循了 Monorepo 的最佳实践，确保测试运行器能够正确解析所有命名空间包的组成部分，避免了难以调试的 `ImportError`。

### 目标
1.  更新根 `pyproject.toml` 的 `[project].dependencies`，使其包含 `pyneedle`。
2.  更新根 `pyproject.toml` 的 `[project.optional-dependencies].dev`，添加 `pyneedle-runtime`。
3.  更新根 `pyproject.toml` 的 `[tool.pytest.ini_options].pythonpath`，添加 `pyneedle` 包的 `src` 目录。

### 基本原理
-   **主依赖**: `pyneedle` 是整个项目的聚合包，它会通过自己的依赖关系拉取 `pointer`, `runtime`, 和 `spec`。因此，在根目录的主依赖中只需要声明 `pyneedle` 即可。
-   **开发依赖**: 开发环境（特别是测试和静态分析）需要直接访问所有子包。因此，在 `[dev]` 依赖中，我们需要明确列出所有 `pyneedle-*` 包，以确保工具链能够发现它们。
-   **测试路径**: `pytest` 需要知道去哪里寻找代码。由于我们使用了 `src` 布局和命名空间包，必须将所有提供 `needle` 命名空间的 `src` 目录都添加到 `pythonpath` 中，这样 `import needle.pointer` 和 `import needle.runtime` 才能在测试期间被正确解析。

### 标签
#intent/tooling #flow/ready #priority/medium #comp/build #scope/dx #ai/instruct #task/domain/build #task/object/dependencies #task/action/refactor #task/state/begin

---

### Script

#### Acts 1: 更新根 pyproject.toml 文件

我将通过一次 `patch` 操作完成对根 `pyproject.toml` 的三处修改：添加主依赖、补全开发依赖和修正 `pytest` 的 `pythonpath`。

~~~~~act
patch_file
pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-monorepo"
version = "0.1.0"
description = "Needle"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "ruff",
    "mypy",
    "pyneedle",
    "pyneedle-pointer",
    "pyneedle-spec",
]

[tool.setuptools.packages.find]
exclude = ["migrations*"]

[tool.uv.workspace]
members = [
    "packages/*",
]

[tool.uv.sources]
pyneedle = { workspace = true }
pyneedle-runtime = { workspace = true }
pyneedle-pointer = { workspace = true }
pyneedle-spec = { workspace = true }

[tool.pytest.ini_options]
addopts = "-ra --cov=needle --cov-report=term-missing"
testpaths = ["tests", "packages"]
norecursedirs = ["tests/fixtures"]
pythonpath = [
    "packages/pyneedle-pointer/src",
    "packages/pyneedle-runtime/src",
    "packages/pyneedle-spec/src",
]

[tool.stitcher.targets.needle]
scan_paths = [
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-monorepo"
version = "0.1.0"
description = "Needle"
requires-python = ">=3.10"
dependencies = [
    "pyneedle",
]

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

[tool.setuptools.packages.find]
exclude = ["migrations*"]

[tool.uv.workspace]
members = [
    "packages/*",
]

[tool.uv.sources]
pyneedle = { workspace = true }
pyneedle-runtime = { workspace = true }
pyneedle-pointer = { workspace = true }
pyneedle-spec = { workspace = true }

[tool.pytest.ini_options]
addopts = "-ra --cov=needle --cov-report=term-missing"
testpaths = ["tests", "packages"]
norecursedirs = ["tests/fixtures"]
pythonpath = [
    "packages/pyneedle/src",
    "packages/pyneedle-pointer/src",
    "packages/pyneedle-runtime/src",
    "packages/pyneedle-spec/src",
]

[tool.stitcher.targets.needle]
scan_paths = [
~~~~~

### 下一步建议

配置已更新。为了验证修改是否生效，我建议你在项目根目录下运行以下命令：
1.  **安装依赖**: `uv pip install -e ".[dev]"`
2.  **运行测试**: `pytest`

如果所有测试都能顺利通过，则证明我们的配置是完整且正确的。
