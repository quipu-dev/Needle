这是因为 PyPI 并不是一个文件服务器，它只是将你指定的 `readme` 文件内容渲染在项目主页上。当你点击 `[中文](./README.zh.md)` 这个相对链接时，浏览器会尝试在 `pypi.org` 的路径下寻找该文件，从而导致 404。

为了让 PyPI 上的用户能够访问到中文文档，我们必须将这些跨语言链接改为**指向 GitHub 的绝对路径**。

## [WIP] fix(docs): 修复 PyPI 上的 README 跨语言链接

### 错误分析
在 `packages/pyneedle/README.md` 中使用了相对路径链接 `[中文](./README.zh.md)`。
*   **在 GitHub 上**: 相对链接可以正常工作，因为它是一个文件浏览器。
*   **在 PyPI 上**: 相对链接失效，因为 PyPI 只托管和渲染主 `README.md` 的内容，并不托管其他 Markdown 文件作为网页。

### 用户需求
修复 PyPI 项目主页上的语言切换链接，确保用户能正确跳转到中文文档。

### 评论
这是分发 Monorepo 项目时的常见问题。在“产品级”文档中，任何指向仓库内其他文件的链接都应该使用绝对 URL，以确保其在不同平台（GitHub, PyPI, 甚至是第三方文档聚合网站）上的可移植性。

### 目标
1.  将 `packages/pyneedle/README.md` 和 `packages/pyneedle/README.zh.md` 中的语言切换链接改为 GitHub 的绝对地址。
2.  提升 `pyneedle` 的版本号以触发更新到 PyPI。

### 基本原理
我们将使用 `patch_file` 替换相对链接为绝对链接。绝对链接指向 `main` 分支下的对应文件。这种做法虽然会让链接指向仓库的最前沿版本，但对于文档来说，这通常是用户期望的。

### 标签
#intent/fix #flow/ready #priority/medium #comp/docs #scope/ux #task/domain/devops #task/object/readme-links #task/action/fix #task/state/continue

---

### Script

#### Acts 1: 修复英文 README 的链接

~~~~~act
patch_file
packages/pyneedle/README.md
~~~~~
~~~~~markdown.old
[English](./README.md) | [中文](./README.zh.md)
~~~~~
~~~~~markdown.new
[English](https://github.com/quipu-dev/Needle/blob/main/packages/pyneedle/README.md) | [中文](https://github.com/quipu-dev/Needle/blob/main/packages/pyneedle/README.zh.md)
~~~~~

#### Acts 2: 修复中文 README 的链接

~~~~~act
patch_file
packages/pyneedle/README.zh.md
~~~~~
~~~~~markdown.old
[English](./README.md) | [中文](./README.zh.md)
~~~~~
~~~~~markdown.new
[English](https://github.com/quipu-dev/Needle/blob/main/packages/pyneedle/README.md) | [中文](https://github.com/quipu-dev/Needle/blob/main/packages/pyneedle/README.zh.md)
~~~~~

#### Acts 3: 提升版本号以触发发布

为了让 PyPI 上的内容更新，我们需要发布一个新的版本。

~~~~~act
patch_file
packages/pyneedle/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle"
version = "0.1.2"
~~~~~
~~~~~toml.new
[project]
name = "pyneedle"
version = "0.1.3"
~~~~~

### 下一步建议
1.  **合并到 main**: 合并后，CD 脚本将检测到 `pyneedle` 版本从 `0.1.1` 变为 `0.1.2`。
2.  **验证发布**: 观察 GitHub Actions 的运行。由于我们的脚本是幂等的，它会跳过 `pyneedle-spec` 等未变动的包，仅发布 `pyneedle`。
3.  **检查 PyPI**: 发布完成后，访问 PyPI 页面，点击“中文”链接，它现在应该能正确跳转到 GitHub 上的中文文档页面。
