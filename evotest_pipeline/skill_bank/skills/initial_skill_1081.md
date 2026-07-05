---
name: mutation-validation-in-batchwriter
description: When testing BatchWriter implementations that accept Mutation objects,
  write tests that pass null mutations and verify that the implementation throws a
  proper checked MutationNotFoundException or IllegalArgumentException. This skill
  covers validating mutation content before writing.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- ARRAY_INDEX_ACCESS
- NULL_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# mutation-validation-in-batchwriter

## Instructions

# Mutation Validation in BatchWriter

## Instructions

- WHEN the TG encounters a BatchWriter implementation that accepts Mutation objects via an `addMutation(Mutation)` method
- THEN it should write a test that passes a null Mutation and verifies that the implementation correctly throws an exception (typically `IllegalArgumentException` or a custom exception like `MutationNotFoundException`)
- WHEN the `addMutation` method accepts mutations that are then validated before storage (e.g., checking if the mutation matches a known set of valid mutations)
- THEN the test should pass a mutation that does NOT match any expected/known mutation, and verify that the implementation throws the appropriate exception
- Include both cases: (1) null Mutation input, and (2) a Mutation that fails internal validation (e.g., the BatchWriter may have logic that checks mutations against a pre-defined set)
- The test should use `assertThrows` with the specific exception class expected (e.g., `assertThrows(IllegalArgumentException.class, () -> writer.addMutation(null))`)
- Common pitfall: Testing only with valid mutations and skipping the null/invalid mutation edge case. Always test what happens when you pass null or an unexpected mutation to `addMutation`.

### Correct Example (Java/JUnit 5):
```java
@Test
public void testNullMutationThrowsException() {
    MockBatchWriter writer = new MockBatchWriter(...);
    assertThrows(IllegalArgumentException.class, () -> writer.addMutation(null));
}
```

### Incorrect Example (does not test the null case):
```java
@Test
public void testAddMutation() {
    MockBatchWriter writer = new MockBatchWriter(...);
    Mutation m = new Mutation("row");
    writer.addMutation(m);
    // Only tests the happy path, no null / invalid mutation test
}
```