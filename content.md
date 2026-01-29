You've correctly identified the issues. My previous generation had a subtle type-safety bug and an incorrect import path. Your analysis is spot on: `I18NFactoryOperator` lives in `needle.operators`, not `needle.runtime`, and the `LogBridge`'s auto-mapping logic was too naive, failing to account for type-based subscriptions which cannot be implicitly converted to a string key for I18n lookup.

I will now generate a plan to fix these two specific errors, making the code both type-safe and correct.

## [WIP] fix: Resolve type errors in pyneedle-bus implementation

### 错误分析

The Pyright type checker has identified two valid issues in the initial implementation of `pyneedle-bus`:

1.  **`bridge.py` Type Mismatch**: The `LogBridge.connect` method incorrectly assumes that any `topic` can be used as a `ptr` (a `SemanticPointer` or string) for the `FeedbackBus`. When a `topic` is a class type (e.g., `RunStartedEvent`), it cannot be used for I18n template lookup. This leads to a `TypeError` when `feedback_bus.present()` is called.
2.  **`store.py` Import Error**: The `MessageStore` attempts to import `I18NFactoryOperator` and `OverlayOperator` from `needle.runtime`. The correct location for these components is the `needle.operators` namespace, which is provided by the `pyneedle-runtime` package.

### 用户需求

1.  Correct the import path in `packages/pyneedle-bus/src/needle/bus/store.py`.
2.  Refactor the logic in `packages/pyneedle-bus/src/needle/bus/bridge.py` to be type-safe, explicitly handling the case where a type-based event is bridged.

### 评论

These fixes are essential for architectural correctness. The first fix ensures that `pyneedle-bus` correctly utilizes the `pyneedle-runtime`'s operator system as intended. The second, more critical fix, makes the `LogBridge` more robust and explicit. It enforces a clear contract: if you subscribe to an event by its *type*, you *must* explicitly provide the `SemanticPointer` to use for its log message, removing ambiguity and preventing runtime errors.

### 目标

1.  Eliminate all Pyright errors in the `pyneedle-bus` package.
2.  Ensure the `LogBridge` raises a helpful `TypeError` during setup if configured incorrectly, rather than failing during event handling.
3.  Enable the integration test `test_unified_bus_integration` to pass without type errors.

### 基本原理

We will use two precise `patch_file` operations:
1.  For `store.py`, we'll perform a simple line replacement of the incorrect import statement.
2.  For `bridge.py`, we will replace the naive `target_ptr = ptr or topic` logic with an `if/elif/else` block that correctly validates the inputs and assigns `target_ptr` in a type-safe manner, raising an error for invalid configurations.

### 标签

#intent/fix #flow/ready #priority/high #comp/bus #concept/type-safety #scope/core #task/domain/bus #task/object/core-implementation #task/action/bug-fix #task/state/continue

---

### Script

#### Acts 1: Correct `MessageStore` Import Path

First, let's fix the incorrect import statement in `store.py`.

~~~~~act
patch_file
packages/pyneedle-bus/src/needle/bus/store.py
~~~~~
~~~~~python
from needle.runtime import I18NFactoryOperator, OverlayOperator
~~~~~
~~~~~python
from needle.operators import I18NFactoryOperator, OverlayOperator
~~~~~

#### Acts 2: Implement Type-Safe Logic in `LogBridge`

Now, we'll patch `bridge.py` to make the `connect` method robust and type-safe.

~~~~~act
patch_file
packages/pyneedle-bus/src/needle/bus/bridge.py
~~~~~
~~~~~python
        target_ptr = ptr or topic
        
        def handler(event: Any):
~~~~~
~~~~~python
        target_ptr: Union[str, SemanticPointerProtocol]

        if ptr is not None:
            # Explicit mapping always wins.
            target_ptr = ptr
        elif not isinstance(topic, type):
            # Auto-bridge for string/pointer topics.
            target_ptr = topic
        else:
            # A type-based topic was given without an explicit pointer. This is an error.
            raise TypeError(
                f"Cannot auto-bridge event type '{getattr(topic, '__name__', 'UnknownType')}'. "
                "An explicit 'ptr' (SemanticPointer) must be provided when connecting a type-based topic."
            )

        def handler(event: Any):
~~~~~

### 下一步建议

The identified errors have been resolved. The `pyneedle-bus` codebase should now be type-correct and logically sound.

The next logical step is to re-run the integration test you defined previously. It should now pass without any issues, confirming that our unified bus architecture works as designed. If you agree, I will re-run the test command.
