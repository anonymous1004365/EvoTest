---
name: property-index-create-session-handling
description: WHEN a PropertyIndexLookup is created with a null or non-existent root/RootProvider,
  THEN the test must verify that the system handles the situation gracefully rather
  than throwing an unexpected NullPointerException. This covers boundary validation
  for PropertyIndexLookup construction and query execution in oak-core index lookups.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# property-index-create-session-handling

## Instructions

# PropertyIndex Create and Session Handling

## Instructions

### WHEN the TG encounters code that constructs a `PropertyIndexLookup` object or passes a `NullPointer` root, or calls methods that depend on the `RootProvider`

- **THEN** the TG must write a test that constructs a `PropertyIndexLookup` with a `null` or invalid root context and verify the behavior is handled gracefully (e.g., returns an empty result, throws a meaningful exception, or handles the case without crashing).
- **Specifically**, tests for `PropertyIndexLookup` and related index classes must verify:
  1. Calling methods like `getIndexCost(...)`, `collectResult(...)` or `query(...)` with a property name that does not exist in the index should not throw `NullPointerException`.
  2. If a `RootProvider` returns `null` for a given `Root`, the calling code should handle it without crashing.
  3. When creating a `PropertyIndexLookup` with a `null` or non-initialized `RootProvider`, the test should verify that an appropriate exception is thrown or empty results are returned.
- **What to verify**: The test should expect a meaningful result (e.g., `Collections.emptyList()`, or a `CommitFailedException`, `IllegalArgumentException`, or `IndexNotFoundException`) rather than an unexpected `NullPointerException`.
- **Common pitfalls**:
  - ❌ Only testing valid/well-formed inputs (e.g., valid property names that exist).
  - ❌ Not testing edge cases like `null` or invalid root contexts.
  - ❌ Assuming that `getIndexCost()` or `collectResult()` will never be called with missing/unknown property names.
  - ❌ Forgetting to test the `PropertyIndexLookup` constructor with null/invalid root parameters.

### Correct Example

```java
// ✅ Correct: Tests that unknown property names in PropertyIndexLookup are handled gracefully
@Test
public void testUnknownPropertyReturnsEmptyResult() throws Exception {
    PropertyIndexLookup lookup = new PropertyIndexLookup(root);
    // Query for a property that doesn't exist in any index
    Set<String> result = lookup.collectResult(PropertyStates.createProperty("nonexistentProp", "value"));
    assertNotNull("Result should not be null", result);
    assertTrue("Result should be empty for unknown property", result.isEmpty());
}
```

### Incorrect Example

```java
// ❌ Incorrect: Only tests with valid/known property names, misses null/invalid root edge cases
@Test
public void testKnownProperty() throws Exception {
    PropertyIndexLookup lookup = new PropertyIndexLookup(root);
    Set<String> result = lookup.collectResult(PropertyStates.createProperty("knownProp", "value"));
    assertTrue("Expected results for known property", result.size() > 0);
    // Missing: tests for unknown properties, null root, etc.
}
```