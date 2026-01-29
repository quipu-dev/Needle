好的，我们将更新 `pyneedle` 的中英文文档，将这次令人兴奋的“多重索引”和“广播机制”补充进去。这不仅能让文档更现代化，也能让新用户一眼看到 `PyNeedle` 在处理复杂资源时的优雅。

## [COMMIT] docs(cli): 更新 README 以展示多重索引与广播语法

### 用户需求
在 `pyneedle` 的 `README.md` 和 `README.zh.md` 中展示最新的指针代数特性：
1. 使用 `L['a', 'b']` 快捷创建集合。
2. 展示 `PointerSet` 的点号（`.`）和索引（`[]`）广播能力。

### 评论
文档是代码的门面。新的语法大大简化了集合创建的视觉复杂度，将其作为“高级用法”中的首推方案，能极大地提升项目的吸引力。

### 目标
1. 更新英文 `README.md` 的 "Pointer Algebra" 章节。
2. 更新中文 `README.zh.md` 的 “指针代数” 章节。
3. 替换过时的 `PointerSet([L.a, L.b])` 构造示例为更优雅的 `L['a', 'b']`。

### 基本原理
通过对比“旧方式”和“新方式”，或者直接展示“新方式”的流畅性，让开发者感受到 DSL 的演进。我们在文档中强调这不仅仅是快捷方式，而是一种“语义寻址协议”的体现。

### 标签
#intent/document #flow/ready #priority/medium
#comp/docs #concept/navigation #scope/ux #scope/dx
#ai/instruct
#task/domain/docs #task/object/readme #task/action/refactor
#task/state/end #task/status/completed

---

### Script

#### Acts 1: 更新英文文档 (README.md)

~~~~~act
patch_file
packages/pyneedle/README.md
~~~~~
~~~~~markdown.old
### Pointer Algebra

Create sets of pointers for powerful, expressive operations.

```python
from needle import L, PointerSet

# Define a set of base pointers
user_fields = PointerSet([L.user.name, L.user.email])

# Broadcast a suffix across the set
form_labels = user_fields / "label"
# Result: PointerSet({L.user.name.label, L.user.email.label})

# Use multiplication for cartesian-product-like expansion
actions = {"read", "write"}
permissions = L.auth.user * actions
# Result: PointerSet({L.auth.user.read, L.auth.user.write})
```
~~~~~
~~~~~markdown.new
### Pointer Algebra

Create sets of pointers for powerful, expressive operations. PyNeedle supports fluent broadcasting and multi-indexing.

```python
from needle import L

# 1. Multi-indexing shortcut
# Create a PointerSet effortlessly
user_fields = L.user['name', 'email']
# Result: PointerSet({L.user.name, L.user.email})

# 2. Attribute & Index Broadcasting
# Broadcast a suffix or index across the entire set fluently
form_labels = user_fields.label
# Result: PointerSet({L.user.name.label, L.user.email.label})

# 3. Cartesian Product Expansion
# Use multiplication to expand a pointer into a set
actions = {"read", "write"}
permissions = L.auth.user * actions
# Result: PointerSet({L.auth.user.read, L.auth.user.write})

# 4. Advanced Chaining
# Combine everything for powerful resource addressing
errors = L.api['v1', 'v2'][404].message
# Result: PointerSet({L.api.v1[404].message, L.api.v2[404].message})
```
~~~~~

#### Acts 2: 更新中文文档 (README.zh.md)

~~~~~act
patch_file
packages/pyneedle/README.zh.md
~~~~~
~~~~~markdown.old
### 指针代数

创建指针集合以进行强大且富有表现力的操作。

```python
from needle import L, PointerSet

# 定义一个基础指针集合
user_fields = PointerSet([L.user.name, L.user.email])

# 在集合的每个成员上广播一个后缀
form_labels = user_fields / "label"
# 结果: PointerSet({L.user.name.label, L.user.email.label})

# 使用乘法进行类似笛卡尔积的扩展
actions = {"read", "write"}
permissions = L.auth.user * actions
# 结果: PointerSet({L.auth.user.read, L.auth.user.write})
```
~~~~~
~~~~~markdown.new
### 指针代数

创建指针集合以进行强大且富有表现力的操作。PyNeedle 支持流畅的广播和多重索引。

```python
from needle import L

# 1. 多重索引快捷方式
# 轻松创建一个指针集合 (PointerSet)
user_fields = L.user['name', 'email']
# 结果: PointerSet({L.user.name, L.user.email})

# 2. 属性与索引广播
# 在整个集合上流畅地广播后缀或索引
form_labels = user_fields.label
# 结果: PointerSet({L.user.name.label, L.user.email.label})

# 3. 笛卡尔积扩展
# 使用乘法将单个指针扩展为集合
actions = {"read", "write"}
permissions = L.auth.user * actions
# 结果: PointerSet({L.auth.user.read, L.auth.user.write})

# 4. 高级链式调用
# 组合所有特性，实现强大的资源寻址
errors = L.api['v1', 'v2'][404].message
# 结果: PointerSet({L.api.v1[404].message, L.api.v2[404].message})
```
~~~~~

#### Acts 3: 提交文档更新

~~~~~act
git_add
packages/pyneedle/README.md
packages/pyneedle/README.zh.md
~~~~~

~~~~~act
git_commit
~~~~~
~~~~~text
docs: update READMEs to showcase multi-indexing and broadcasting

Updated both English and Chinese READMEs to reflect the latest pointer
algebra features. Replaced the legacy 'PointerSet' constructor example
with the more elegant 'L[a, b]' shortcut and demonstrated the power
of attribute/index broadcasting.
~~~~~

### 下一步建议
- **Stitcher 同步**: 既然运行时已经支持了这些语法，如果你还在维护 `Stitcher`（代码生成工具），可能需要检查其生成的 Stub 文件是否能与这种多态的 `__getitem__` 完美配合。
- **发布新版本**: 如果所有测试和文档都已就绪，现在可以考虑正式发布 `0.1.4` 版本了。
