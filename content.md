# 📸 Snapshot Capture

### 💬 备注:
stitcher

检测到工作区发生变更。

### 📝 变更文件摘要:
```
packages/pyneedle-bus/src/needle/bus/bridge.py     | 16 ----
 .../src/needle/bus/bridge.stitcher.yaml            | 13 ++++
 packages/pyneedle-bus/src/needle/bus/event.py      | 23 ------
 .../src/needle/bus/event.stitcher.yaml             | 19 +++++
 packages/pyneedle-bus/src/needle/bus/feedback.py   | 24 ------
 .../src/needle/bus/feedback.stitcher.yaml          | 21 +++++
 packages/pyneedle-bus/stitcher.lock                | 90 ++++++++++++++++++++++
 .../pyneedle-pointer/src/needle/pointer/core.py    |  6 --
 .../src/needle/pointer/core.stitcher.yaml          |  5 ++
 packages/pyneedle-pointer/stitcher.lock            |  5 ++
 .../pyneedle-pointer/tests/test_pointer_algebra.py |  8 +-
 .../pyneedle-spec/src/needle/spec/protocols.py     |  2 +-
 packages/pyneedle-spec/stitcher.lock               |  8 +-
 pyproject.toml                                     |  1 +
 14 files changed, 165 insertions(+), 76 deletions(-)
```