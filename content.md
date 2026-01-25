好的，所有的配置工作已经完成。我们已经成功修正了元数据、解决了构建路径问题，并部署了自动化的发布工作流。

现在，我将生成一个 `[COMMIT]` 计划，将这些基础设施的变更打包为一个完整的逻辑单元进行提交。

## [COMMIT] chore: 配置 PyPI 发布元数据与 GitHub Action 自动化工作流

### 用户需求

将所有为了支持 PyPI 发布而进行的 `pyproject.toml` 变更以及新创建的 GitHub Action 工作流提交到 Git 仓库。

### 评论

这次提交标志着 Needle 项目从一个本地开发仓库正式转变为一个具备分发能力和自动化 CI/CD 流程的工业级库。通过将所有环境配置一次性提交，我们确保了仓库状态的确定性和可追溯性。

### 目标

1.  将根目录及 4 个子包的 `pyproject.toml` 修改加入暂存区。
2.  将 `.github/workflows/python-publish.yml` 加入暂存区。
3.  创建一个符合 Conventional Commits 规范的、信息详尽的提交记录。

### 基本原理

遵循“正规军”工程标准，我们将所有基础设施变更视为一个整体。通过 `[COMMIT]` 类型的计划，我们显式地完成了从“构建阶段”到“交付阶段”的转换。

### 标签

#intent/tooling #flow/ready #priority/high #comp/build #concept/executor #scope/dx #ai/instruct #task/domain/tooling #task/object/release-automation #task/action/commit #task/state/end #task/status/completed

---

### Script

#### Acts 1: 提交基础设施变更

我们将暂存所有相关的配置文件并执行提交。

~~~~~act
git_add
pyproject.toml
packages/pyneedle-spec/pyproject.toml
packages/pyneedle-pointer/pyproject.toml
packages/pyneedle-runtime/pyproject.toml
packages/pyneedle/pyproject.toml
.github/workflows/python-publish.yml
~~~~~

~~~~~act
git_commit
~~~~~
~~~~~text
chore: configure PyPI publishing and GitHub Action CD workflow

This commit prepares the monorepo for official distribution on PyPI.

Changes:
- Added comprehensive metadata (authors, license, classifiers, urls) to all pyproject.toml files.
- Fixed PEP 508 dependency syntax by removing illegal quotes around version strings.
- Resolved build issues in monorepo sub-packages by removing absolute path references to root README.md.
- Implemented a GitHub Action workflow (.github/workflows/python-publish.yml) to automatically build and publish all 5 packages to PyPI upon pushing a version tag (v*).

The project is now ready for versioned releases.
~~~~~

### 下一步建议

- **触发发布**: 现在你可以通过执行 `git push origin main --tags` 来触发你的第一次正式发布（前提是你已经按照之前的建议打了标签）。
- **文档同步**: 既然子包移除了 `readme` 字段，后续可以考虑编写一个简单的脚本，在发布前自动将根目录的 `README.md` 拷贝到各个子包，或者为每个子包编写更具针对性的文档。
- **验证 OIDC**: 如果你有兴趣，下一步我们可以配置 GitHub Actions 的“可信发布者 (Trusted Publishing)”，这样你就无需在 GitHub 中维护 `PYPI_API_TOKEN` 这个 Secret 了，安全性更高。
