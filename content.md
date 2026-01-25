既然测试发布已经圆满成功，现在是时候建立自动化的持续部署（CD）流程了。我们将创建一个 GitHub Action，当你推送以 `v` 开头的标签（例如 `v0.1.0`）时，它会自动构建并发布 monorepo 中的所有 5 个软件包。

## [WIP] feat: 创建 GitHub Action 自动发布工作流

### 用户需求

创建一个 GitHub Action 配置文件，实现以下自动化流程：
1.  **触发条件**: 仅在推送版本标签（如 `v0.1.0`）时触发。
2.  **构建逻辑**: 构建 monorepo 中的所有 5 个软件包。
3.  **发布逻辑**: 使用存储在 GitHub Secrets 中的 API Key 将所有构建产物上传到 PyPI。

### 评论

对于 Monorepo 项目，自动化发布不仅是提升开发者体验（DX）的手段，更是确保版本一致性的必要工具。手动发布多个包极易出错，而通过 CI 确保每一个标签都对应一组完整的、经过验证的包，是维持生态系统稳定性的最佳实践。

### 目标

1.  在项目根目录下创建 `.github/workflows/python-publish.yml`。
2.  配置工作流以使用 `uv` 进行快速构建。
3.  配置发布步骤，使其能够处理 `dist/` 目录下的多个包产物。

### 基本原理

我们将使用官方推荐的 `pypa/gh-action-pypi-publish` 操作，因为它原生支持多包发布且具有良好的错误重试机制。工作流会首先确保环境中有最新的 `uv`，然后执行与我们之前手动操作相同的构建序列。最终，所有在 `dist/` 目录中生成的 `.whl` 和 `.tar.gz` 文件都会被批量上传。

### 标签

#intent/build #flow/ready #priority/high #comp/build #concept/executor #scope/dx #ai/instruct #task/domain/tooling #task/object/github-action-cd #task/action/implementation #task/state/continue

---

### Script

#### Acts 1: 创建 GitHub 工作流目录及配置文件

我们将首先创建必要的目录结构，然后写入 YAML 配置文件。请确保你在 GitHub 仓库的 **Settings > Secrets and variables > Actions** 中创建了一个名为 `PYPI_API_TOKEN` 的 Secret，并填入你的 PyPI Token。

~~~~~act
run_command
~~~~~
~~~~~
mkdir -p .github/workflows
~~~~~

~~~~~act
write_file
.github/workflows/python-publish.yml
~~~~~
~~~~~yaml
name: Upload Python Package

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.10"

    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh

    - name: Build packages
      run: |
        # 依次构建所有组件，产物将存放在根目录的 dist/
        uv build packages/pyneedle-spec
        uv build packages/pyneedle-pointer
        uv build packages/pyneedle-runtime
        uv build packages/pyneedle
        uv build .

    - name: Publish all packages to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        user: __token__
        password: ${{ secrets.PYPI_API_TOKEN }}
        # 如果你希望发布到 TestPyPI 进行验证，可以启用以下行
        # repository-url: https://test.pypi.org/legacy/
~~~~~

### 下一步建议

1.  **配置密钥**: 请务必确认 GitHub 仓库中已配置名为 `PYPI_API_TOKEN` 的 Secret。
2.  **首次发布**: 你可以尝试创建一个新标签并推送来触发此流程：
    ```bash
    git add .github/workflows/python-publish.yml
    git commit -m "chore: add automated publishing workflow"
    git tag v0.1.0
    git push origin main --tags
    ```
3.  **安全性建议**: PyPI 现在支持基于 GitHub Actions 的 **Trusted Publishing (OIDC)**，这比使用长期有效的 API Token 更安全且无需手动配置 Secret。如果未来你希望进一步提升安全性，我可以指导你切换到该模式。
