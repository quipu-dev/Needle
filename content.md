好的，我将为所有 `pyproject.toml` 文件添加必要的元数据，以便将这些软件包发布到 PyPI。

这包括添加作者信息、许可证、仓库 URL、分类器，并为工作区内的依赖项指定确切的版本。

## [WIP] chore: 为 PyPI 发布配置软件包

### 用户需求

为项目中的所有 `pyproject.toml` 文件（包括根目录和 `packages/` 下的每个包）添加发布到 PyPI 所需的元数据。

### 评论

这是将 Needle 库提供给更广泛的 Python 社区的关键一步。正确配置的元数据可以提高包的可发现性、可信度和易用性，是发布的最佳实践。

### 目标

1.  更新根目录以及 `pyneedle`、`pyneedle-spec`、`pyneedle-pointer`、`pyneedle-runtime` 四个包的 `pyproject.toml` 文件。
2.  在每个文件的 `[project]` 部分中添加 `authors`, `license`, `readme`, `classifiers`, `keywords` 字段。
3.  添加 `[project.urls]` 部分，链接到项目主页、代码仓库和问题跟踪器。
4.  将内部依赖项（如 `pyneedle-spec`）的版本固定为 `'0.1.0'`，以确保在 PyPI 上可以正确解析。

### 基本原理

我们将使用 `patch_file` 对每个 `pyproject.toml` 文件进行精确修改。这种方法可以确保我们只更新 `[project]` 部分，而不会影响 `[tool.uv.workspace]` 或 `[tool.hatch.build.targets.wheel]` 等其他重要的构建和开发配置。通过为每个包添加完整的元数据，可以确保它们在 PyPI 上被正确索引和展示。

### 标签

#intent/tooling #flow/ready #priority/high #comp/build #concept/config #scope/dx #ai/instruct #task/domain/tooling #task/object/pypi-publish #task/action/configuration #task/state/begin

---

### Script

#### Acts 1: 配置根 `pyproject.toml`

首先，我们为根元包添加发布信息。

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
dependencies = [
    "pyneedle",
]
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-monorepo"
version = "0.1.0"
description = "Needle"
readme = "README.md"
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle == '0.1.0'",
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
keywords = ["semantic", "pointer", "needle", "i18n", "configuration"]

[project.urls]
Homepage = "https://github.com/quipu-dev/Needle"
Repository = "https://github.com/quipu-dev/Needle"
"Bug Tracker" = "https://github.com/quipu-dev/Needle/issues"
~~~~~

#### Acts 2: 配置 `pyneedle-spec` 包

接下来，配置 `pyneedle-spec`，这是所有其他包的基础。

~~~~~act
patch_file
packages/pyneedle-spec/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-spec"
version = "0.1.0"
description = "Core protocols and specifications for the PyNeedle ecosystem."
requires-python = ">=3.10"
dependencies = []
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-spec"
version = "0.1.0"
description = "Core protocols and specifications for the PyNeedle ecosystem."
readme = "../../README.md"
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = []
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
keywords = ["semantic", "pointer", "needle", "i18n", "configuration", "spec", "protocol"]

[project.urls]
Homepage = "https://github.com/quipu-dev/Needle"
Repository = "https://github.com/quipu-dev/Needle"
"Bug Tracker" = "https://github.com/quipu-dev/Needle/issues"
~~~~~

#### Acts 3: 配置 `pyneedle-pointer` 包

然后，配置 `pyneedle-pointer` 包。

~~~~~act
patch_file
packages/pyneedle-pointer/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-pointer"
version = "0.1.0"
description = "Standard implementation of Semantic Pointers (L) for PyNeedle."
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec",
]
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-pointer"
version = "0.1.0"
description = "Standard implementation of Semantic Pointers (L) for PyNeedle."
readme = "../../README.md"
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec == '0.1.0'",
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
keywords = ["semantic", "pointer", "needle", "i18n", "configuration"]

[project.urls]
Homepage = "https://github.com/quipu-dev/Needle"
Repository = "https://github.com/quipu-dev/Needle"
"Bug Tracker" = "https://github.com/quipu-dev/Needle/issues"
~~~~~

#### Acts 4: 配置 `pyneedle-runtime` 包

配置 `pyneedle-runtime` 包。

~~~~~act
patch_file
packages/pyneedle-runtime/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-runtime"
version = "0.1.0"
description = "Core runtime for the PyNeedle ecosystem."
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec",
    "pyneedle-pointer",
]
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-runtime"
version = "0.1.0"
description = "Core runtime for the PyNeedle ecosystem."
readme = "../../README.md"
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec == '0.1.0'",
    "pyneedle-pointer == '0.1.0'",
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
keywords = ["semantic", "pointer", "needle", "i18n", "configuration", "runtime", "operator"]

[project.urls]
Homepage = "https://github.com/quipu-dev/Needle"
Repository = "https://github.com/quipu-dev/Needle"
"Bug Tracker" = "https://github.com/quipu-dev/Needle/issues"
~~~~~

#### Acts 5: 配置 `pyneedle` 主包

最后，配置 `pyneedle` 这个“全家桶”包。

~~~~~act
patch_file
packages/pyneedle/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle"
version = "0.1.0"
description = "Batteries-included distribution of the PyNeedle runtime."
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec",
    "pyneedle-pointer",
    "pyneedle-runtime",
]
~~~~~
~~~~~toml.new
[project]
name = "pyneedle"
version = "0.1.0"
description = "Batteries-included distribution of the PyNeedle runtime."
readme = "../../README.md"
authors = [
    { name = "doucx", email = "doucxldh@gmail.com" },
]
license = { text = "Apache-2.0" }
requires-python = ">=3.10"
dependencies = [
    "pyneedle-spec == '0.1.0'",
    "pyneedle-pointer == '0.1.0'",
    "pyneedle-runtime == '0.1.0'",
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
keywords = ["semantic", "pointer", "needle", "i18n", "configuration"]

[project.urls]
Homepage = "https://github.com/quipu-dev/Needle"
Repository = "https://github.com/quipu-dev/Needle"
"Bug Tracker" = "https://github.com/quipu-dev/Needle/issues"
~~~~~

### 下一步建议

所有 `pyproject.toml` 文件现已配置完毕。

接下来，你可以按照标准流程进行打包和上传：
1.  **清理旧的构建文件**: `rm -rf dist build *.egg-info`
2.  **构建所有包**: `python -m build` (或者使用 `uv` `build` 命令)
3.  **上传到 PyPI**: `twine upload dist/*`

请确保你已经使用 `twine` 登录到了你的 PyPI 账户。
