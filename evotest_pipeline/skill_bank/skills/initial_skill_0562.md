---
name: creator-nondup-verification-return-guard
description: When a validation method (like verifyNonDup) changes from void to boolean
  return (indicating whether the creator should be used), the caller must guard state
  mutation behind the return value. Without this guard, duplicate creators can overwrite
  valid creator state, causing deserialization failures.
code_tags:
- VALIDATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# creator-nondup-verification-return-guard

## Instructions

# Creator Duplicate Verification Return Value Guarding

## Instructions

- WHEN the TG encounters a method that validates duplicates or conflicts (like `verifyNonDup(creator, typeIndex, explicit)`) and its return type has been changed from `void` to `boolean` (where `false` means "skip, don't use this creator")
- THEN the TG MUST test that when `verifyNonDup` returns `false` (e.g. because a more specific creator already exists), the caller does NOT update internal creator state fields (like `_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`)
- WHEN testing property-based creators (e.g. `addPropertyCreator`), verify that providing a duplicate constructor/static factory that is less explicit does NOT overwrite the previously registered creator's properties
- WHEN testing delegate creators (e.g. `addStringDelegateCreator`), verify that the delegate type-specific fields (`_arrayDelegateArgs` vs `_delegateArgs`) are only updated when the new creator is accepted
- The test should verify correct behavior by attempting deserialization with a JSON input matching the more-specific creator's properties AFTER a less-specific duplicate creator attempt has been registered
- Common pitfalls:
  - Testing only the happy path where no duplicates exist
  - Not verifying that state fields remain unchanged after a rejected duplicate creator
  - Assuming that calling `verifyNonDup` with a duplicate simply returns without side effects (the bug was that `verifyNonDup` returned `void` and the caller unconditionally updated state)

### Correct Example (tests the guard):
```java
// Test: duplicate less-explicit creator does NOT overwrite property-based creator
@Test
public void testDuplicateCreatorDoesNotOverwriteProperties() {
    ObjectMapper mapper = new ObjectMapper();
    // SimplePojo has two constructors - one explicit (all-args) and one implicit (no-arg)
    // Ensure the explicit one is not overwritten
    SimplePojo result = mapper.readValue("{\"intField\": 1, \"stringField\": \"foo\"}", SimplePojo.class);
    assertEquals(1, result.intField);
    assertEquals("foo", result.stringField);
}
```

### Incorrect Example (would pass on buggy code but should fail on fixed):
```java
// BAD: Only tests that no exception is thrown; does NOT verify correct deserialization behavior
@Test
public void testDuplicateCreatorNoException() {
    // This test would pass even with buggy code because no exception occurs
    // It does not verify the actual behavior is correct
}
```