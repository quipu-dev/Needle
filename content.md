# 📸 Snapshot Capture

检测到工作区发生变更。

### 📝 变更文件摘要:
```
.gitignore                                         | 211 +++++++++++++++++++++
 LICENSE                                            | 201 ++++++++++++++++++++
 README.md                                          | 193 +++++++++++++++++++
 README.zh.md                                       | 193 +++++++++++++++++++
 packages/pyneedle-pointer/pyproject.toml           |  18 ++
 packages/pyneedle-pointer/src/needle/__init__.py   |   1 +
 .../src/needle/pointer/__init__.py                 |  18 ++
 .../src/needle/pointer/__init__.stitcher.yaml      |   2 +
 .../pyneedle-pointer/src/needle/pointer/core.py    |  68 +++++++
 .../src/needle/pointer/core.stitcher.yaml          |  28 +++
 .../pyneedle-pointer/src/needle/pointer/set.py     |  21 ++
 .../src/needle/pointer/set.stitcher.yaml           |  15 ++
 packages/pyneedle-pointer/stitcher.lock            |  93 +++++++++
 .../pyneedle-pointer/tests/test_pointer_algebra.py | 151 +++++++++++++++
 .../tests/test_pointer_algebra.stitcher.yaml       |  18 ++
 packages/pyneedle-runtime/pyproject.toml           |  20 ++
 packages/pyneedle-runtime/src/needle/__init__.py   |   1 +
 .../src/needle/loaders/json_handler.stitcher.yaml  |   6 +
 .../src/needle/loaders/protocols.stitcher.yaml     |   6 +
 .../src/needle/operators/__init__.py               |  11 ++
 .../src/needle/operators/dict_operator.py          |  29 +++
 .../needle/operators/dict_operator.stitcher.yaml   |   7 +
 .../src/needle/operators/fs_operator.py            |  48 +++++
 .../src/needle/operators/fs_operator.stitcher.yaml |  17 ++
 .../src/needle/operators/helpers/json_handler.py   |  70 +++++++
 .../src/needle/operators/helpers/protocols.py      |  10 +
 .../src/needle/operators/i18n_factory.py           |  25 +++
 .../needle/operators/i18n_factory.stitcher.yaml    |   7 +
 .../src/needle/operators/overlay_operator.py       |  19 ++
 .../operators/overlay_operator.stitcher.yaml       |   7 +
 ...
 50 files changed, 2737 insertions(+)
```