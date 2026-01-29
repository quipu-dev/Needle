好的，既然 `pyneedle-bus` 发生了重大的架构变更（删除了 `MessageStore`），我们应当提升其版本号。考虑到目前处于 `0.1.x` 阶段，我们将版本号提升至 `0.1.1`。

## [WIP] chore(bus): 提升 pyneedle-bus 版本号至 0.1.1

### 用户需求
更新 `pyneedle-bus` 的版本号以反映其架构重构。

### 标签
#intent/tune #flow/ready #priority/low
#comp/bus #comp/build
#task/domain/bus
#task/object/versioning
#task/action/update
#task/state/continue

---

### Script

#### Acts 1: 更新 pyproject.toml 版本号

~~~~~act
patch_file
packages/pyneedle-bus/pyproject.toml
~~~~~
~~~~~toml.old
[project]
name = "pyneedle-bus"
version = "0.1.0"
description = "Unified EventBus (logic) and FeedbackBus (presentation) for the PyNeedle ecosystem."
~~~~~
~~~~~toml.new
[project]
name = "pyneedle-bus"
version = "0.1.1"
description = "Unified EventBus (logic) and FeedbackBus (presentation) for the PyNeedle ecosystem."
~~~~~

### 下一步建议
我们已经完成了 `pyneedle-bus` 侧的所有修正。现在，我们可以开始处理 **Stitcher** 侧的适配工作了。

由于 `pyneedle-bus` 0.1.1 不再包含 `MessageStore`，`stitcher-common` 中的 `bus.py` 目前处于损坏状态。

我建议下一个计划的任务是：**重构 `stitcher-common` 的总线组装逻辑**。我们将把原先在 `MessageStore` 中的资产加载和语言检测逻辑，“下沉”到 Stitcher 自己的 `bus.py` 中，并手动完成 `FeedbackBus` 的初始化和注入。
