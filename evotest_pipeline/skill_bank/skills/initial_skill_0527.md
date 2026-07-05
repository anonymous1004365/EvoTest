---
name: template-parameter-type-validation
description: When a Builder or creator method accepts a template/proxy parameter that can contain different element types, the TG should validate that the builder correctly processes elements of all supported types (e.g., both String and CtTypeReference), not just one type, and should test that deserialization works end-to-end when the builder's internal state is affected by these types.
code_tags: ['TEMPLATE_PARAMETER_VALIDATION']
test_pattern: STATE_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a `CreatorCollector` or similar builder/creator class that collects `SettableBeanProperty` instances from a template or proxy parameter (e.g., a `List<?>` of parameters where each element could be of type `String` or `CtTypeReference` or other types)
- THEN the TG should write a test that creates instances with **different element types** in the template parameter collection and verifies that:
  1. The builder correctly processes each type without throwing an exception
  2. The resulting object can be deserialized/serialized end-to-end with both types tested
  3. The test should use `ObjectMapper` to round-trip a JSON payload and verify the deserialized object's state matches expectations
- Common pitfalls to avoid:
  - **Testing only one parameter type** (e.g., only `String` type parameters when the code also supports `CtTypeReference` or other types)
  - **Not testing the end-to-end deserialization** — verifying only that the builder doesn't crash is insufficient; the test must confirm the built object deserializes correctly with the expected values
  - **Assuming all template parameter types are equivalent** — different types may trigger different code paths in the builder's internal logic

### Example (Correct)

```java
// Test handles template parameters of different types  
public class CreatorTemplateParameterTest {
    static class SimplePojo {
        public int intField;
        public String stringField;
        
        @JsonCreator
        public SimplePojo(@JsonProperty("intField") int intField,
                          @JsonProperty("stringField") String stringField) {
            this.intField = intField;
            this.stringField = stringField;
        }
    }
    
    @Test
    public void testBothTypesWork() throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        // Both int and String template parameters should be resolved correctly
        SimplePojo result = mapper.readValue(
            "{ \"intField\": 42, \"stringField\": \"hello\" }", 
            SimplePojo.class
        );
        assertEquals(42, result.intField);
        assertEquals("hello", result.stringField);
    }
}
```

### Example (Incorrect)

```java
// BAD: Only tests String-type parameters, missing int/other types
@Test
public void testOnlyStringParameters() throws Exception {
    // This test passes even if the builder fails on non-String types
    ObjectMapper mapper = new ObjectMapper();
    String result = mapper.readValue("\"just a string\"", String.class);
    assertEquals("just a string", result);
}
```