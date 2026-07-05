---
name: creator-duplicate-resolution-order
description: When a class has multiple constructors/factory methods (creators), and
  a duplicate is encountered, the buggy code used to unconditionally overwrite with
  the new creator. The fix makes verifyNonDup return a boolean so callers only replace
  when the return is true. TG should test this by providing a POJO with multiple constructors
  to ensure the first explicit/annotated creator is chosen, not overwritten.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# creator-duplicate-resolution-order

## Instructions

# Creator Duplicate Resolution Order

## Instructions

- WHEN the TG encounters code that registers "creators" (constructors/factory methods) for a class, and duplicate creators may arise (e.g., multiple constructors or factory methods for the same class)
- THEN the TG should write a test that:
  1. Defines a POJO with **two constructors** — one explicitly annotated (e.g., `@JsonCreator`) and one implicit or with different visibility
  2. Deserializes JSON that maps to the *less specific* creator and verifies the *more specific* or *explicitly annotated* creator is actually used
  3. Verifies that no `JsonMappingException` is thrown (the bug was a `JsonMappingException` when the wrong creator got overwritten and the fields didn't match)
  4. Specifically uses the `ObjectMapper` to deserialize and assert the correct field values
- **Concrete example from the bug**: The buggy `CreatorCollector.addPropertyCreator()` called `verifyNonDup()` (which returned void) and then unconditionally overwrote `_propertyBasedArgs`. The fix wraps the assignment in `if (verifyNonDup(...)) { ... }`. A test should create a POJO like `SimplePojo` with both `(int intField, String stringField)` and `(String stringField, int intField)` constructors, annotate one with `@JsonCreator`, and verify deserialization of `{"intField": 1, "stringField": "foo"}` succeeds.
- **Common pitfalls**: 
  - Testing only a single constructor — the bug only manifests with multiple creators where one is explicitly marked
  - Forgetting that `verifyNonDup` is a *side-effect* method that was changed to return a boolean; the test must trigger the duplicate scenario
  - Using `@JsonCreator` without specifying which properties go to which constructor params — the test should rely on implicit/name-based matching to trigger the duplicate resolution

### Correct test structure (pseudocode)
```java
@Test
public void testConstructorChoice() throws Exception {
    // POJO has two constructors; one annotated with @JsonCreator
    // The bug caused the wrong constructor's property mapping to be used
    String json = "{\"intField\": 1, \"stringField\": \"foo\"}";
    SimplePojo result = MAPPER.readValue(json, SimplePojo.class);
    assertEquals(1, result.intField);
    assertEquals("foo", result.stringField);
}
```

### Incorrect test structure
```java
// BAD: tests only one constructor or a scenario without duplicate resolution
@Test
public void testSimpleConstructor() throws Exception {
    // Only one creator exists — doesn't exercise verifyNonDup
    SimplePojo result = MAPPER.readValue("{\"a\":1}", SimplePojo.class);
    assertEquals(1, result.a);
}
```