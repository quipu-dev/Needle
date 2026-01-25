根据 **“作用域标签 (Scoped Tags)”** 的设计模式，我将更新 GitHub Action。

这种模式是处理 Monorepo 独立发布的工业标准。它允许你通过 `pyneedle-spec@v0.1.1` 这样的标签，精准触发特定子包的构建与发布，而不会干扰其他包。

## [WIP] feat: 升级 GitHub Action 以支持 Scoped Tags 独立发布

### 用户需求

修改 `.github/workflows/python-publish.yml`，使其支持通过 `*@v*` 格式的标签进行按需发布：
1.  **标签解析**: 从标签中自动提取包名（例如从 `pyneedle-spec@v0.1.1` 中提取 `pyneedle-spec`）。
2.  **按需构建**: 仅构建标签指定的那个子包，而不是构建所有包。
3.  **独立发布**: 将构建出的唯一产物发布到 PyPI。

### 评论

这是 Monorepo 走向成熟的必经之路。独立发布减少了不必要的版本跳变，降低了发布风险，并使得版本历史更加清晰。虽然这要求开发者遵循特定的标签规范，但带来的自动化收益和架构清晰度是巨大的。

### 目标

1.  更新 `on.push.tags` 为 `*@v*`。
2.  在工作流中增加一个解析步骤，识别包名。
3.  动态决定构建路径（`packages/<pkg_name>` 或根目录）。
4.  确保发布前清理 `dist/`，保证上传的只有当前标签对应的包。

### 基本原理

通过 shell 脚本处理 `${{ github.ref_name }}`。我们利用 `@` 符号作为分隔符。
*   标签: `pyneedle-spec@v0.1.1`
*   解析出的包名: `pyneedle-spec`
*   构建命令: `uv build packages/pyneedle-spec`

如果解析出的包名在 `packages/` 下找不到对应的目录，脚本将回退到构建根目录（用于发布元包）。

### 标签

#intent/tooling #flow/ready #priority/high #comp/build #concept/executor #scope/dx #ai/instruct #task/domain/tooling #task/object/github-action-scoped-publish #task/action/refactor #task/state/continue

---

### Script

#### Acts 1: 更新 GitHub Action 配置文件

我们将使用 `write_file` 完全覆盖旧的配置，引入新的解析和动态构建逻辑。

~~~~~act
write_file
.github/workflows/python-publish.yml
~~~~~
~~~~~yaml
name: Upload Python Package

on:
  push:
    tags:
      - '*@v*'

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

    - name: Parse Scoped Tag
      id: parse
      run: |
        # 标签格式示例: pyneedle-spec@v0.1.1
        TAG_NAME=${{ github.ref_name }}
        PKG_NAME=$(echo $TAG_NAME | cut -d'@' -f1)
        VERSION=$(echo $TAG_NAME | cut -d'@' -f2)
        
        echo "Detected Package: $PKG_NAME"
        echo "Detected Version: $VERSION"
        
        # 将包名导出到后续步骤
        echo "pkg_name=$PKG_NAME" >> $GITHUB_OUTPUT

    - name: Build specific package
      run: |
        PKG_NAME=${{ steps.parse.outputs.pkg_name }}
        
        # 清理之前的产物（如果有）
        rm -rf dist/
        
        # 动态决定构建路径
        if [ -d "packages/$PKG_NAME" ]; then
          echo "Building sub-package: $PKG_NAME"
          uv build packages/$PKG_NAME
        else
          echo "Package directory not found in packages/, building root project..."
          uv build .
        fi

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        user: __token__
        password: ${{ secrets.PYPI_API_TOKEN }}
~~~~~

### 下一步建议

1.  **测试新规范**: 尝试为 `spec` 包打一个新标签：
    ```bash
    git tag pyneedle-spec@v0.1.1
    git push origin pyneedle-spec@v0.1.1
    ```
2.  **观察 Actions 面板**: 确保它正确解析了包名，并只在 `dist/` 中生成了 `pyneedle-spec` 的文件。
3.  **版本同步提示**: 别忘了在打标签前，手动（或使用我们讨论过的脚本）更新 `packages/pyneedle-spec/pyproject.toml` 中的 `version` 字段，使之与标签中的版本号保持一致。PyPI 会拒绝版本号重复的上传。

这种方式完美解决了你“不希望所有包一起更新”的担忧。如果你觉得这种打标签的方式太繁琐，未来我们可以进一步编写一个本地脚本来一键完成“改号+打标+推送”的动作。
