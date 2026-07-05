---
name: creator-duplicate-resolver-guard
description: When a method resolves between multiple candidate constructors/factory
  methods and previously overwrote the winning creator unconditionally, teach the
  TG to verify that when verifyNonDup returns false (i.e. the existing creator should
  be kept), the fields _arrayDelegateArgs, _delegateArgs, and _propertyBasedArgs are
  NOT overwritten. The test should use a POJO with multiple constructors and confirm
  deserialization picks the correct one.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# creator-duplicate-resolver-guard

## Instructions

# Creator Duplicate Resolver Guard

## Instructions

- WHEN the TG encounters code that calls `verifyNonDup(creator, typeIndex, explicit)` and then conditionally assigns `_arrayDelegateArgs`, `_delegateArgs`, or `_propertyBasedArgs` based on the return value (as in `if (verifyNonDup(...)) { ... assign ... }`)
- THEN the TG should write a test that verifies that when a more specific/delegate creator already exists (e.g., an explicit constructor is already registered), a later generic constructor does NOT overwrite the previously chosen creator's injectables. The test must:
  1. Define a POJO class with at least two constructors: one taking a single `Collection`-like type (e.g., `List<String>`) to trigger the `C_ARRAY_DELEGATE` or `C_DELEGATE` path, and one taking multiple properties to trigger the `C_PROPS` path.
  2. Ensure one constructor is explicitly annotated (e.g., `@JsonCreator`) and the other is implicit, so `verifyNonDup` returns `false` for the implicit one.
  3. Attempt to deserialize a JSON payload that should match the property-based constructor (e.g., `{"intField": 1, "stringField": "foo"}`).
  4. Assert that deserialization succeeds without `JsonMappingException` and produces the expected POJO instance.
- Common pitfalls:
  - Testing only a single constructor path — the bug manifests when multiple creators compete and the wrong one wins.
  - Not verifying that the previously chosen creator's injectables (`_delegateArgs`, `_arrayDelegateArgs`, `_propertyBasedArgs`) are preserved when `verifyNonDup` returns `false`.
  - Assuming the fix only relates to `addPropertyCreator` — the same pattern was also fixed in `addStringDelegateCreator` (array delegate and delegate branches).

### Correct example (detects the bug):
```java
// SimplePojo with @JsonCreator on property constructor forces it to be chosen
static class SimplePojo {
    int intField;
    String stringField;
    
    public SimplePojo(@JsonProperty("intField") int intField, 
                       @JsonProperty("stringField") String stringField) {
        this.intField = intField;
        this.stringField = stringField;
    }
}

@Test
public void testConstructorChoice() throws Exception {
    String json = "{\"intField\": 1, \"stringField\": \"foo\"}";
    SimplePojo result = MAPPER.readValue(json, SimplePojo.class);
    assertEquals(1, result.intField);
    assertEquals("foo", result.stringField);
}
```

### Incorrect example (does NOT exercise the bug):
```java
// Only testing one constructor — won't trigger the duplicate resolution logic
@Test
public void testSingleConstructor() throws Exception {
    String json = "{\"intField\": 1}";
    // No competing constructor exists, so verifyNonDup never returns false
    SimplePojo result = MAPPER.readValue(json, SimplePojo.class);
}
```