---
name: stateful-operator-class-cast-on-restore
description: When testing stateful operators with checkpointing/restore functionality,
  verify that type casting during state restoration does not produce ClassCastException
  when state values are deserialized from byte arrays. This skill helps catch type
  mismatches where restored state objects are cast without prior type validation.
code_tags:
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# stateful-operator-class-cast-on-restore

## Instructions

# Stateful Operator Restore Type Casting

## Instructions

- WHEN the TG encounters code that uses a state backend (e.g., `FsStateBackend`, `RocksDBStateBackend`) with a stateful operator that stores state values as byte arrays and restores them via type casting (e.g., `(String)`, `(Long)`)
- THEN the TG should write a **state restore test** that:
  1. Creates an operator with a state descriptor using `ValueStateDescriptor`
  2. Processes some data to set state values
  3. Creates a second operator instance that takes a restored state snapshot (via `OperatorSnapshotResult` or similar)
  4. Calls `initializeState()` on the second operator to simulate restore from checkpoint
  5. Verifies that restored state values can be read back **without throwing ClassCastException**
  6. Tests with **both** primitive wrapper types (e.g., `Long`) and string types as state values
  7. Specifically verify that `valueState.value()` does NOT throw `ClassCastException` after restore
- Common pitfalls:
  - Only testing state save, not state restore (most important: test what happens when state is read back)
  - Testing only one type of state value when multiple types may be stored
  - Not catching `ClassCastException` as the expected failure in the buggy version
  - Forgetting to use the same `TypeSerializer` for both save and restore paths

- **Correct example** (catches bug):
```java
@Test
public void testStatefulOperatorRestoreTypeSafety() throws Exception {
    StreamOperatorFactory<String> factory = ...;
    // Create first operator and set state
    try (StreamTaskMailboxTestHarness<String> harness = ...) {
        harness.processElement(new StreamRecord<>("hello", 0L));
        // Take snapshot
        OperatorSnapshotResult snapshot = harness.snapshot(0L, 0L);
    }
    
    // Restore into second operator
    try (StreamTaskMailboxTestHarness<String> harness2 = ...) {
        harness2.streamTask.restore(snapshot);
        KeyedStateStore stateStore = harness2.streamTask.getKeyedStateStore();
        
        ValueStateDescriptor<String> descriptor = new ValueStateDescriptor<>("state", Types.STRING);
        ValueState<String> state = stateStore.getPartitionedState("testKey", descriptor);
        
        // Should NOT throw ClassCastException
        String value = state.value();
        assertNotNull(value);
    }
}
```

- **Incorrect example** (misses the bug):
```java
// Only tests saving, not restoring — will not catch ClassCastException on restore
@Test
public void testStatefulOperatorSave() throws Exception {
    try (StreamTaskMailboxTestHarness<String> harness = ...) {
        harness.processElement(new StreamRecord<>("data", 1L));
        harness.snapshot(0L, 0L);
        // No restore test!
    }
}
```