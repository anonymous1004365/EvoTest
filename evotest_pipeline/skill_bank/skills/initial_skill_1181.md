---
name: creator-duplicate-resolution
description: When multiple constructors or factory methods exist and the resolver's
  verifyNonDup method incorrectly overwrites the first creator's properties (especially
  _propertyBasedArgs) with the second's, the skills teaches to test that constructor
  resolution respects explicit vs implicit annotations and preserves the chosen creator's
  property bindings.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# creator-duplicate-resolution

## Instructions

# Creator Duplicate Resolution Skill

## Instructions

- WHEN the TG encounters code where `CreatorCollector.addPropertyCreator()` or `addStringCreator()`/`addDelegatingCreator()` is called multiple times for the same creator type index (e.g., `C_PROPS`, `C_DELEGATE`, `C_ARRAY_DELEGATE`), and `verifyNonDup()` is used to determine whether the new or old creator should be retained
- THEN the TG should write a test that:
  - Defines a POJO with two constructors/factory methods — one explicitly annotated with a Jackson creator annotation (e.g., `@JsonCreator`, `@JsonProperty`), and another implicit (no annotation) that also matches the same creator type
  - Deserializes JSON that targets the explicit creator's property names (e.g., `{"intField": 1, "stringField": "foo"}`)
  - Calls `ObjectMapper.readValue(json, PojoClass.class)` and expects it to succeed without throwing `JsonMappingException`
  - Verifies that the deserialized object has the correct property values from the explicitly annotated constructor
  - ALSO tests the reverse scenario (two explicit creators with different parameter types) and expects the more specific one to be chosen

- WHEN the TG sees that `verifyNonDup()` used to be `void` and unconditionally overwrote `_propertyBasedArgs`, `_delegateArgs`, or `_arrayDelegateArgs` even when it decided to keep the old creator
- THEN the TG should write a regression test that:
  - Creates a situation where the first caller to `addPropertyCreator()` has an explicit creator and the second caller has a non-explicit one, or where the first creator's parameter type is more specific than the second's
  - Verifies that after both calls, the first creator's properties (not the second's) are the ones used for deserialization
  - The test should fail on buggy code with `JsonMappingException` containing "Could not find creator property with name ..."

- Common pitfalls to avoid:
  - Testing only with a single constructor — the bug only manifests when there are TWO or more matching creators
  - Testing only with explicit annotations on both constructors — the bug manifests with one explicit and one implicit creator, where the implicit creator's properties incorrectly overwrite the explicit one's
  - Forgetting to check that the deserialized object has correct field values, not just that no exception is thrown
  - Assuming `verifyNonDup()` return value is boolean — buggy version had it as void with unconditional field assignments

### Example: Correct pattern (test that catches the bug)

```java
// POJO with two constructors: explicit (annotated) and implicit
static class SimplePojo {
    int intField;
    String stringField;
    
    @JsonCreator
    public SimplePojo(@JsonProperty("intField") int intField, 
                      @JsonProperty("stringField") String stringField) {
        this.intField = intField;
        this.stringField = stringField;
    }
    
    // Implicit constructor that may override the above
    public SimplePojo(int intField) {
        this.intField = intField;
        this.stringField = "default";
    }
}

// Test
public void testConstructorChoice() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    // This should use the explicit @JsonCreator constructor
    SimplePojo result = mapper.readValue(
        "{\"intField\": 1, \"stringField\": \"foo\"}", 
        SimplePojo.class);
    assertEquals(1, result.intField);
    assertEquals("foo", result.stringField);
}
```

### Example: Incorrect pattern (would miss the bug)

```java
// Incorrect: Only one constructor — no duplicate resolution happening
static class SimplePojo {
    int intField;
    
    @JsonCreator
    public SimplePojo(@JsonProperty("intField") int intField) {
        this.intField = intField;
    }
}

// Incorrect: Tests only that no exception is thrown, not that values are correct
@Test
public void testDeserialization() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    // This might pass on buggy version if the wrong constructor is used
    mapper.readValue("{\"intField\": 1}", SimplePojo.class); // no assertion on values!
}
```