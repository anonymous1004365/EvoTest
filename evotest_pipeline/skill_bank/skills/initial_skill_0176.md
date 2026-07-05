---
name: ignition-event-handler-validation
description: Teaches the TG to write tests that verify IgnitionEventHandler correctly
  handles various device command types and invalid/null state transitions.
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# ignition-event-handler-validation

## Instructions

# IgnitionEventHandler Validation

## Instructions

- WHEN the TG encounters an IgnitionEventHandler that processes device commands or triggers based on position/motion data:
  - THEN it should write a parametric test that verifies each command type (e.g., String commands vs. CtTypeReference-based commands) is handled correctly by the handler.
  - The test should verify that the handler does NOT throw unexpected exceptions when processing commands of different types.
  - Include test cases that pass both valid and invalid/malformed commands to ensure proper validation.
  - Common pitfall: testing only one command type (e.g., String), which misses bugs when other types like CtTypeReference are used.

- WHEN the handler checks device state transitions (e.g., ignition on/off, motion start/stop):
  - THEN the test should verify specific state transitions and ensure that duplicate or out-of-order events do not trigger incorrect behavior.
  - Include edge cases such as null device IDs, null command objects, or missing position data.
  - Common pitfall: assuming the handler silently ignores all invalid input without verifying the actual behavior.

### Correct (Example)
```java
@Test
@ParameterizedTest
@MethodSource("testIgnitionEventHandler")
public void testIgnitionEventHandler(String commandType, Object command) {
    IgnitionEventHandler handler = new IgnitionEventHandler();
    assertThrows(IllegalArgumentException.class, () -> handler.handleCommand(commandType, command));
}
```

### Incorrect (Example)
```java
@Test
public void testIgnitionEventHandler() {
    IgnitionEventHandler handler = new IgnitionEventHandler();
    // Only testing String type, missing the bug
    handler.handleCommand("ignition_on", "someCommand");
    assertTrue(true);
}
```