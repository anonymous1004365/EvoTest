---
name: creator-verification-return-value-check
description: When a method signature changes from void to boolean to indicate success/failure, callers that ignore the return value may corrupt internal state by overwriting existing creators. Use this skill to test that de-duplication logic is correctly respected by callers.
code_tags: ['VALIDATION', 'CREATOR_DEDUP_VERIFICATION']
test_pattern: STATE_TEST
---

# creator-verification-return-value-check

## Instructions

# Creator Verification Return Value Check

## Instructions

- WHEN the TG encounters code where a `void` method like `verifyNonDup(AnnotatedWithParams, int, boolean)` has been changed to return `boolean`, and its callers unconditionally proceed with state mutation (e.g., `_propertyBasedArgs = properties` or `_delegateArgs = injectables`) after calling it
- THEN the TG should write a test that verifies the caller respects the return value of the verification method. Specifically:
  - Create a test scenario where a duplicate (or conflicting) creator is registered after an explicit/annotated creator already exists
  - Assert that the duplicate creator does NOT overwrite the explicit one — i.e., the second call's state mutations (`_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`) should NOT take effect when `verifyNonDup` returns `false`
  - Example: Register an explicit constructor via `@JsonCreator`, then register another constructor (non-explicit) that conflicts. Verify that the explicit constructor's properties are retained, and that deserialization with the conflicting constructor fails with a `JsonMappingException` (e.g., "Could not find creator property with name 'intField'")
- Common pitfalls to avoid:
  - Do NOT test only the happy path where a single creator is registered
  - Do NOT assume that calling `verifyNonDup` alone is sufficient; test that the caller actually guards its state mutations with the return value
  - Do NOT test the `verifyNonDup` method in isolation — test the integration between the verifier and its callers (e.g., `addPropertyCreator`, `addDelegatingCreator`, `addArrayDelegatingCreator`)

### Correct example (testing the bug):
```java
// Buggy behavior: A non-explicit constructor overwrites an explicit one
// because addPropertyCreator ignores the verifyNonDup return value.
// Expected: Deserialization fails with JsonMappingException
// because the explicit constructor's properties are lost.
@Test
public void testConstructorChoice() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    // SimplePojo has @JsonCreator on one constructor and another constructor without annotation
    String json = "{\"intField\": 1, \"stringField\": \"foo\"}";
    try {
        mapper.readValue(json, SimplePojo.class);
        fail("Expected JsonMappingException due to creator property loss");
    } catch (JsonMappingException e) {
        assertTrue(e.getMessage().contains("Could not find creator property with name 'intField'"));
    }
}
```

### Incorrect example (missing the bug):
```java
// This test only checks the happy path and won't catch the bug:
@Test
public void testSingleConstructor() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    String json = "{\"value\": 42}";
    MyPojo result = mapper.readValue(json, MyPojo.class);
    assertEquals(42, result.getValue());
}
```