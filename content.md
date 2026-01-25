好的，我们已经完成了根目录配置的优化。现在我将生成一个 `[COMMIT]` 计划，将这些更改提交到 Git 仓库。

## [COMMIT] chore: 完善项目根依赖配置与测试路径

### 用户需求
将之前对 `pyproject.toml` 的修改创建为一个 Git 提交。

### 评论
这是一次常规的维护提交，确保了项目的根配置与当前的子包结构保持同步，提升了环境安装和测试运行的可靠性。

### 目标
1.  将修改后的 `pyproject.toml` 添加到 Git 暂存区。
2.  创建一个具有清晰描述的 Git 提交。

### 基本原理
遵循原子提交原则，将配置文件的优化作为一个独立的逻辑单元记录在版本历史中。

### 标签
#intent/tooling #flow/ready #priority/medium #comp/build #scope/dx #ai/instruct #task/domain/build #task/object/dependencies #task/action/refactor #task/state/end #task/status/completed

---

### Script

#### Acts 1: 执行 Git 提交

我们将暂存 `pyproject.toml` 文件并提交。

~~~~~act
git_add
pyproject.toml
~~~~~

~~~~~act
git_commit
~~~~~
~~~~~text
chore: update root dependencies and pytest pythonpath

- Add 'pyneedle' to the main project dependencies in root pyproject.toml.
- Add 'pyneedle-runtime' to the dev optional-dependencies.
- Add 'packages/pyneedle/src' to the pytest pythonpath to ensure correct namespace resolution during testing.

These changes improve the onboarding experience by allowing 'pip install .' to work as expected and ensuring tests can be run from the root without import errors.
~~~~~

### 下一步建议
- **CI 验证**: 如果你有配置 CI (如 GitHub Actions)，现在可以推送代码以验证新的依赖配置是否能通过自动化构建。
- **环境刷新**: 建议团队成员运行 `uv sync` 或相应的安装命令来同步最新的依赖配置。
