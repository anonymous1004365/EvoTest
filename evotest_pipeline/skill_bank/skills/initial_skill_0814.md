---
name: mutable-object-format-caching
description: When a message class caches the formatted string of a mutable object
  parameter, tests must verify that the cached value is not affected by later mutations
  of the original object. This skill applies to any class implementing Message that
  caches toString() or formatted output.
code_tags:
- CONCURRENCY
- RESOURCE_MANAGEMENT
- STATE_MUTATION
- MUTABLE_OBJECT_CACHING
test_pattern: STATE_TEST
---

# mutable-object-format-caching

## Instructions

# Mutable Object Format Caching Verification

## Instructions

- WHEN the TG encounters a message class (implementing `Message`, `StringBuilderFormattable`, or similar) that caches a formatted string representation of an object parameter (e.g., storing `String.valueOf(obj)` or `obj.toString()` in a field like `objectString`)
- THEN it should write a test that:
  1. Creates a **mutable** object (e.g., `Mutable`, `StringBuilder`, `AtomicReference`, or any object whose `toString()` changes when its internal state changes)
  2. Constructs the message with that mutable object
  3. Calls `getFormattedMessage()` to trigger caching
  4. **Mutates** the original object (e.g., `param.set("XYZ")`, `charSequence.setLength(0)`)
  5. Calls `getFormattedMessage()` again and asserts it returns the **initial** (cached) value, not the mutated value
  6. If there is a `formatTo(StringBuilder)` method, similarly verify it uses the cached value after mutation

- Concrete example from `ObjectMessage`:
  ```java
  // CORRECT: verifies caching works against mutable objects
  final Mutable param = new Mutable().set("abc");
  final ObjectMessage msg = new ObjectMessage(param);
  msg.getFormattedMessage();        // triggers cache: objectString = "abc"
  param.set("XYZ");                 // mutate the original object
  final String actual = msg.getFormattedMessage();
  assertEquals("Should use initial param value", "abc", actual);
  ```

  ```java
  // CORRECT: also verify formatTo uses cached string
  final StringBuilder charSequence = new StringBuilder("initial value");
  final ObjectMessage message = new ObjectMessage(charSequence);
  assertEquals("initial value", message.getFormattedMessage());
  charSequence.setLength(0);
  charSequence.append("different value");
  final StringBuilder result = new StringBuilder();
  message.formatTo(result);
  assertEquals("initial value", result.toString());
  ```

- Common pitfalls to avoid:
  - **Testing only after mutation but before first call**: This tests the "unsafe" path (reflecting latest value) rather than the caching path. You must call `getFormattedMessage()` BEFORE mutating to trigger the cache.
  - **Using immutable objects like `String` or `BigDecimal`**: These don't change, so they can't expose caching bugs. Use mutable objects like `StringBuilder`, `Mutable`, or custom mutable classes.
  - **Forgetting to test `formatTo`**: If the class has both `getFormattedMessage()` and `formatTo()`, both should use the cached value after caching is triggered.
  - **Only testing after the second `getFormattedMessage()` call**: The key step is mutating between the first and second call — without mutation between calls, the bug won't surface.
  - **Not checking that the cached value equals the initial (pre-mutation) value**: The assertion should check `assertEquals("initial value", actual)`, not `assertNotEquals("XYZ", actual)` which is weaker.