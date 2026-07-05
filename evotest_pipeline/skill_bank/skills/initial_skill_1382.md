---
name: creator-collector-return-type-mismatch
description: When a method's return type changes from void to boolean without updating
  all callers, the caller may silently ignore the return value and miss the intended
  behavior change. Use this skill when the code shows void-to-boolean signature changes
  in builder/setter methods.
code_tags:
- VOID_TO_BOOLEAN_RETURN_CHANGE
test_pattern: INTERACTION_TEST
---

# creator-collector-return-type-mismatch

## Instructions

# CreatorCollector Return Type Mismatch Skill

## Instructions

- WHEN the TG encounters a method whose return type was changed from `void` to `boolean` (e.g., `setX(...)` → `setX(...) returning boolean`), and the method is called by other methods in the same class without checking the return value
- THEN the TG should write an interaction test that:
  1. Creates an instance of the containing class
  2. Calls the method with the void-to-boolean return type change on that instance
  3. Verifies that the return value is `false` (or the expected sentinel value) when the operation fails or encounters invalid input
  4. Verifies that the return value is `true` (or the expected sentinel value) when the operation succeeds
  5. The test should assert the boolean return value explicitly, not just check side effects
- The bug occurs because calling code treats the method as if it still returns `void`, ignoring the boolean result that indicates success/failure
- Common pitfalls to avoid:
  - Testing only the side effects (e.g., checking that a field was set) without verifying the return value
  - Assuming the return value is always `true` without testing both branches
  - Writing a test that would pass on both the buggy and fixed versions (it must fail on the buggy version to be valuable)
  - Not testing the specific combination of parameters that triggers the ignored return value code path

### Example (Correct Test)

```java
// Correct: explicitly tests boolean return value
@Test
public void testCreateUsingArrayDelegatesReturnsFalseForInvalidInput() {
    CreatorCollector collector = new CreatorCollector(...);
    boolean result = collector.createUsingArrayDelegates(invalidInput);
    assertFalse("Should return false for invalid input when return type is boolean", result);
    // Also test the successful case
    boolean successResult = collector.createUsingArrayDelegates(validInput);
    assertTrue("Should return true for valid input", successResult);
}
```

### Example (Incorrect Test)

```java
// Incorrect: treats method as void, only checks side effects
@Test
public void testCreateUsingArrayDelegates() {
    CreatorCollector collector = new CreatorCollector(...);
    collector.createUsingArrayDelegates(someInput);
    // No assertion on return value — this test would pass on both buggy and fixed versions
    assertNotNull(collector.someField);
}
```