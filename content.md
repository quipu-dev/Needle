这是一个典型的语法错误。在 `pyproject.toml` 的 `dependencies` 列表中，版本号不应该被额外的单引号包围。PEP 508 规范要求格式为 `package == version`（例如 `pyneedle == 0.1.0`），而不是 `package == '0.1.0'`。

此外，我注意到在子包中引用 `../../README.md` 可能在打包发布时导致路径问题（因为打包后的目录结构会发生变化）。

我将立即修正所有文件中的 PEP 508 依赖语法。

## [WIP] fix: 修正 pyproject.toml 中的 PEP 508 依赖语法错误

### 错误分析

在 `pyproject.toml` 的 `dependencies` 数组中，我错误地将版本号写成了 `"package == '0.1.0'"`。
根据 **PEP 508** 规范，版本说明符不需要内部引号。`uv build` 调用的 `setuptools` 校验器正确地识别并拦截了这一非法格式。

### 用户需求

修正所有 `pyproject.toml` 文件中的依赖声明，确保符合 PEP 508 标准，使 `uv build` 能够顺利通过。

### 评论

这是一个基础的格式错误。在 TOML 字符串中，内容会被直接作为 PEP 508 表达式解析。通过移除内部单引号，我们可以消除歧义并使配置合法化。

### 目标

1.  移除根目录 `pyproject.toml` 中 `pyneedle` 依赖的单引号。
2.  移除 `pyneedle-pointer`、`pyneedle-runtime` 和 `pyneedle` 子包中所有内部依赖版本号的单引号。

### 基本原理

使用 `patch_file` 对受影响的行进行精确替换。我们将 `"package == '0.1.0'"` 修正为 `"package == 0.1.0"`。

### 标签

#intent/fix #flow/ready #priority/high #comp/build #concept/config #scope/dx #ai/instruct #task/domain/tooling #task/object/pypi-publish #task/action/fix-syntax #task/state/continue

---

### Script

#### Acts 1: 修正根目录依赖

~~~~~act
patch_file
pyproject.toml
~~~~~
~~~~~toml.old
dependencies = [
    "pyneedle == '0.1.0'",
]
~~~~~
~~~~~toml.new
dependencies = [
    "pyneedle == 0.1.0",
]
~~~~~

#### Acts 2: 修正 `pyneedle-pointer` 依赖

~~~~~act
patch_file
packages/pyneedle-pointer/pyproject.toml
~~~~~
~~~~~toml.old
dependencies = [
    "pyneedle-spec == '0.1.0'",
]
~~~~~
~~~~~toml.new
dependencies = [
    "pyneedle-spec == 0.1.0",
]
~~~~~

#### Acts 3: 修正 `pyneedle-runtime` 依赖

~~~~~act
patch_file
packages/pyneedle-runtime/pyproject.toml
~~~~~
~~~~~toml.old
dependencies = [
    "pyneedle-spec == '0.1.0'",
    "pyneedle-pointer == '0.1.0'",
]
~~~~~
~~~~~toml.new
dependencies = [
    "pyneedle-spec == 0.1.0",
    "pyneedle-pointer == 0.1.0",
]
~~~~~

#### Acts 4: 修正 `pyneedle` 依赖

~~~~~act
patch_file
packages/pyneedle/pyproject.toml
~~~~~
~~~~~toml.old
dependencies = [
    "pyneedle-spec == '0.1.0'",
    "pyneedle-pointer == '0.1.0'",
    "pyneedle-runtime == '0.1.0'",
]
~~~~~
~~~~~toml.new
dependencies = [
    "pyneedle-spec == 0.1.0",
    "pyneedle-pointer == 0.1.0",
    "pyneedle-runtime == 0.1.0",
]
~~~~~

### 下一步建议

语法现已修正。你可以再次运行 `uv build`。

**注意**: 如果构建仍然报错关于找不到 `../../README.md`（因为部分构建工具在打包子包时不允许引用父目录文件），你可能需要考虑将 README 拷贝到每个子包目录下，或者在 `pyproject.toml` 中暂时移除 `readme` 字段或将其指向本地存在的文件。但目前的优先事项是解决 PEP 508 的语法阻断。
