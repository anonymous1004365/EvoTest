---
name: creator-verification-return-value-check
description: When verifying creator methods (constructors/factories) with a return
  value from verifyNonDup, always guard property assignments behind the verification
  result. Without checking the return value, the wrong creator's properties can overwrite
  the correct one, causing deserialization failures.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# creator-verification-return-value-check

## Instructions

# Creator Verification Return Value Guarding

## Instructions

- WHEN the TG encounters code that calls `verifyNonDup(creator, typeIndex, explicit)` or similar non-duplicate verification methods AND subsequently assigns properties or arguments (e.g., `_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`),
- THEN it should write a test that provides MULTIPLE constructors/factory methods annotated with `@JsonCreator`, where at least one is more specific and one is more generic (e.g., one taking an `int` field and another taking `String`), and verify that the correct creator is selected and its properties are used for deserialization.
- Specifically, when two `@JsonCreator` constructors exist (one annotated explicitly, one not), verify that deserialization using the explicit one succeeds and produces the expected field values. On the buggy version, the test should expect a `com.fasterxml.jackson.databind.JsonMappingException` with message containing `"Could not find creator property with name"`.
- Common pitfalls:
  - Testing only a single constructor (no ambiguity to resolve) — the bug only manifests when multiple creators exist and `verifyNonDup` returns `false` for the later one but its properties still overwrite the earlier one's.
  - Not using `@JsonCreator` annotations on both constructors — the explicit annotation is what triggers the verification path that can incorrectly replace properties.
  - Only checking that deserialization succeeds — must verify the field values are correct (from the right constructor), not just that no exception is thrown.

**Correct test example:**
```java
// POJO with two @JsonCreator constructors; the 1-arg constructor should be used
static class SimplePojo {
    int intField;
    String stringField;

    @JsonCreator
    public SimplePojo(@JsonProperty("intField") int intField,
                      @JsonProperty("stringField") String stringField) {
        this.intField = intField;
        this.stringField = stringField;
    }

    @JsonCreator
    public SimplePojo(@JsonProperty("intField") String intField) {
        this.intField = Integer.parseInt(intField);
    }

    // No-arg constructor shouldn't be needed, but add getters...
}

@Test
public void testConstructorChoice() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    String json = "{\"intField\": 1, \"stringField\": \"foo\"}";
    SimplePojo result = mapper.readValue(json, SimplePojo.class);
    assertEquals(1, result.intField);
    assertEquals("foo", result.stringField);
}
```

**Incorrect test example (no multiple creators, only trivial test):**
```java
// Only one constructor — no ambiguity, so no bug
static class SimplePojo {
    int intField;
    @JsonCreator
    public SimplePojo(@JsonProperty("intField") int intField) {
        this.intField = intField;
    }
}
@Test
public void testSimple() throws Exception {
    // This passes even in buggy version — doesn't catch the issue
    SimplePojo r = new ObjectMapper().readValue("{\"intField\": 42}", SimplePojo.class);
}
```