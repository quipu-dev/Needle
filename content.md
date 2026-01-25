好的，正如预期的那样，构建后端（`hatchling`）在处理子包时无法解析指向父目录之外的 `../../README.md`。按照你的要求，我将移除所有子包中的 `readme` 字段。

## [WIP] chore: 移除子包中的 readme 字段以解决构建路径问题

### 错误分析

当在子目录中运行构建（如 `uv build packages/pyneedle`）时，构建后端会将该子目录视为构建上下文的根。由于 `../../README.md` 位于该上下文之外，`hatchling` 出于安全和封装考虑无法访问该文件，从而导致 `OSError: Readme file does not exist`。

### 用户需求

从所有位于 `packages/` 目录下的子包的 `pyproject.toml` 中移除 `readme` 字段，以消除构建阻断。

### 评论

对于多包仓库（Monorepo），通常需要将 README 显式拷贝到每个包的目录下，或者在发布脚本中进行处理。暂时移除该字段是最快恢复构建能力的方案。

### 目标

1.  从以下文件中移除 `readme = "../../README.md"` 行：
    *   `packages/pyneedle-spec/pyproject.toml`
    *   `packages/pyneedle-pointer/pyproject.toml`
    *   `packages/pyneedle-runtime/pyproject.toml`
    *   `packages/pyneedle/pyproject.toml`

### 基本原理

通过 `patch_file` 移除该配置行。由于根目录的 `pyproject.toml` 指向的是同级目录下的 `README.md`，因此无需修改根目录文件。

### 标签

#intent/tooling #flow/ready #priority/high #comp/build #concept/config #scope/dx #ai/instruct #task/domain/tooling #task/object/pypi-publish #task/action/fix-config #task/state/continue

---

### Script

#### Acts 1: 移除 `pyneedle-spec` 的 readme 字段

~~~~~act
patch_file
packages/pyneedle-spec/pyproject.toml
~~~~~
~~~~~toml.old
description = "Core protocols and specifications for the PyNeedle ecosystem."
readme = "../../README.md"
authors = [
~~~~~
~~~~~toml.new
description = "Core protocols and specifications for the PyNeedle ecosystem."
authors = [
~~~~~

#### Acts 2: 移除 `pyneedle-pointer` 的 readme 字段

~~~~~act
patch_file
packages/pyneedle-pointer/pyproject.toml
~~~~~
~~~~~toml.old
description = "Standard implementation of Semantic Pointers (L) for PyNeedle."
readme = "../../README.md"
authors = [
~~~~~
~~~~~toml.new
description = "Standard implementation of Semantic Pointers (L) for PyNeedle."
authors = [
~~~~~

#### Acts 3: 移除 `pyneedle-runtime` 的 readme 字段

~~~~~act
patch_file
packages/pyneedle-runtime/pyproject.toml
~~~~~
~~~~~toml.old
description = "Core runtime for the PyNeedle ecosystem."
readme = "../../README.md"
authors = [
~~~~~
~~~~~toml.new
description = "Core runtime for the PyNeedle ecosystem."
authors = [
~~~~~

#### Acts 4: 移除 `pyneedle` 的 readme 字段

~~~~~act
patch_file
packages/pyneedle/pyproject.toml
~~~~~
~~~~~toml.old
description = "Batteries-included distribution of the PyNeedle runtime."
readme = "../../README.md"
authors = [
~~~~~
~~~~~toml.new
description = "Batteries-included distribution of the PyNeedle runtime."
authors = [
~~~~~

### 下一步建议

现在子包的配置已精简，你可以再次尝试 `uv build packages/pyneedle` 或在根目录运行构建。构建通过后，这些包就可以顺利发布到 PyPI 了。
