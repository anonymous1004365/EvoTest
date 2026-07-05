---
name: data-supplier-cache-state-null-check
description: When a data supplier has internal caches (like precomputed elements)
  that are lazily initialized and cleared via a reset/clear method, tests must ensure
  that calling getter methods before initialization does not produce stale or null
  values. This skill helps catch NullPointerExceptions or stale-state bugs in supplier/pool
  patterns.
code_tags:
- NULL_CHECK
- STATE_TRANSITION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# data-supplier-cache-state-null-check

## Instructions

# Data Supplier Cache State Null Safety

## Instructions

- WHEN the TG encounters a data supplier class that maintains internal caches (e.g., `List`, `Map`, or array fields holding precomputed elements like `dataSupplier`, `inputMaskPairs`, `soCKeys`, `storage`, etc.) with a `reset` or `clear` method that sets those caches back to a "not yet initialized" state (e.g., setting them to `null` or clearing them)
- THEN the TG must write a test that:
  1. Calls a method that triggers lazy initialization of the caches (e.g., `getInputMask` or `getNextInputMask`, `getNextData`, `getSecretSharedKey`, etc.)
  2. Then calls the reset/clear method (e.g., `reset()`, `clearAll()`)
  3. **Then** calls the getter method again
  4. Verifies that the call does NOT throw a `NullPointerException` and returns a valid (non-null) result or behaves gracefully

- Common pitfalls:
  - Testing only the happy path where caches are initialized once and never reset
  - Forgetting to test the state transition: initialized → reset → re-initialized
  - Assuming that a reset simply empties collections and getters check for empty, when in fact the field might be set to `null` and getters fail with NPE
  - Testing reset with only one type of cached element (e.g., only testing `getInputMask` after reset but not `getNextData` or other getters)

- Example (correct):
```java
@Test(expected = ...) // Remove expected if method should handle gracefully
public void testGetNextInputMaskAfterReset() {
    // Arrange
    ConfigurableDataSupplier dataSupplier = new ConfigurableDataSupplier(...);
    // Act — first call initializes the cache
    dataSupplier.getNextInputMask(1);  // or getInputMask(...)
    // Reset clears the internal state
    dataSupplier.reset();
    // Assert — second call should not throw NPE
    dataSupplier.getNextInputMask(1);  // Must NOT throw NullPointerException
}
```

- Example (incorrect — misses the reset):
```java
@Test
public void testGetNextInputMask() {
    ConfigurableDataSupplier dataSupplier = new ConfigurableDataSupplier(...);
    dataSupplier.getNextInputMask(1);  // Only tests initial call, never tests after reset
    // This would not catch the post-reset NPE bug
}
```

- Example (incorrect — wrong expectation):
```java
@Test(expected = NullPointerException.class)
public void testGetNextInputMaskAfterReset() {
    ConfigurableDataSupplier dataSupplier = new ConfigurableDataSupplier(...);
    dataSupplier.getNextInputMask(1);
    dataSupplier.reset();
    dataSupplier.getNextInputMask(1);  // If the fix makes this valid, expecting NPE is wrong
}
```