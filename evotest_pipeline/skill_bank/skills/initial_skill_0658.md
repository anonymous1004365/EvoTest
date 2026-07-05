---
name: checkpoint-stateful-operator-restoration
description: ''
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- NULL_CHECK
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# checkpoint-stateful-operator-restoration

## Instructions

# Checkpoint Stateful Operator Restoration

## Instructions

WHEN the TG encounters code that involves:
- Stateful operators being restored from savepoints or checkpoints (e.g., `TimelyStatefulOperator`, operators with `.uid("...")`)
- Savepoint migration tests that load state from a previous Flink version savepoint
- Operator state that includes timers, keyed state, or list/union state

THEN the TG should:
1. **Verify state restoration correctness**: After restoring from a savepoint, the operator should behave identically to one that reached the same state naturally. Test that the operator processes events correctly post-restoration (e.g., timers fire, state values are correct).
2. **Test with multiple state types**: Include tests for different state types — value state, list state, map state, and timers — to ensure each is properly restored.
3. **Check recovery from edge cases**: Test restoration after failures during checkpointing, or when the savepoint contains state for operators that no longer exist (or vice versa).
4. **Validate operator UID matching**: Ensure that the operator UID used during savepoint creation matches the UID used during restoration — mismatches should throw an appropriate exception.
5. **Test with and without state changes**: Verify that operators that mutated state before the savepoint are still in that mutated state after restoration (e.g., counters that were incremented, timers that were registered).

**Common pitfalls to avoid:**
- ❌ Testing only the savepoint/restore mechanism without verifying the operator's actual behavior post-restoration (e.g., just checking that no exception is thrown).
- ❌ Assuming that all state types are restored correctly without explicitly testing each type used by the operator.
- ❌ Using hardcoded state values without asserting that they match the expected values from the savepoint.
- ❌ Forgetting to verify that timers registered before the savepoint fire at the correct time after restoration.

**Correct example:**
```java
@Test
public void testOperatorStateRestoration() throws Exception {
    // Create an operator, register state and timers
    TimelyStatefulOperator op = new TimelyStatefulOperator();
    // ... set up, trigger some state mutations, create savepoint
    // Restore from savepoint
    // After restoration:
    assertThat(op.getStateValue()).isEqualTo(EXPECTED_VALUE);
    // Trigger a watermark to fire timers
    op.processWatermark(new Watermark(TIMER_TIME));
    assertThat(op.getTimerFired()).isTrue();
}
```

**Incorrect example:**
```java
@Test
public void testOperatorStateRestoration() throws Exception {
    // Just restores without verifying behavior
    // No check on state values or timer firing after restore
    // No assertion about post-restoration processing
    restoreFromSavepoint(operator, savepoint);
    // Missing: operator behavior assertions
}
```