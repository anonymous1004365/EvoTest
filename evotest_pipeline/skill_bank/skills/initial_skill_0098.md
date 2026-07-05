---
name: creator-nondup-overwrite-guard
description: When a method is changed from void to returning a boolean to indicate
  whether a creator should be registered, the TG should test that a new creator does
  not overwrite an existing explicitly-marked creator when the new one is not explicit.
  This skill prevents bugs where method calls that previously always executed (void)
  now conditionally execute based on a return value.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# creator-nondup-overwrite-guard

## Instructions

# Creator Non-Dup Overwrite Guard

## Instructions

WHEN a method like `verifyNonDup` (or similar duplicate-registration checking) is changed from `void` to returning `boolean`, and callers are changed from unconditionally executing to conditionally executing based on the return value, THEN:

- **Test that explicitly marked creators are not overwritten** by non-explicit (implicitly discovered) creators that would have previously overwritten them. Create a POJO class with multiple constructors — one explicitly annotated with `@JsonCreator` and one implicit (unannotated). Deserialize with `ObjectMapper` and verify the result uses the explicitly marked constructor.

- **Test the specific parameter types and properties** of the chosen constructor. The `verifyNonDup` logic selects between creators based on `explicit` flag and parameter type assignability. The test should verify both that the correct creator is chosen and that the correct property values are set.

- **Expect `JsonMappingException`** on the buggy version if the implicitly discovered creator overwrites an explicit one, because the overwritten creator's properties become inaccessible. The error message will contain: `"Could not find creator property with name '...'"`.

Common pitfalls to avoid:
- **Testing only a single constructor/creator**: You must test the scenario where multiple constructors compete (one explicit, one implicit) to trigger the overwrite bug.
- **Testing only happy path**: You must test that when `verifyNonDup` returns `false` (because an explicit creator already exists), the caller correctly skips registering the implicit creator.
- **Forgetting to verify properties of the resulting object**: Simply checking that no exception is thrown is insufficient — verify that the deserialized object contains the correct property values from the explicitly chosen creator.

**Correct example pattern:**
```java
public class SimplePojo {
    private String stringField;
    private int intField;

    @JsonCreator
    public SimplePojo(@JsonProperty("stringField") String stringField) {
        this.stringField = stringField;
    }

    // Implicit (no annotation) — competing creator
    public SimplePojo(@JsonProperty("intField") int intField) {
        this.intField = intField;
    }
}

public void testExplicitCreatorNotOverwritten() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    String json = "{\"intField\": 1, \"stringField\": \"foo\"}";
    SimplePojo result = mapper.readValue(json, SimplePojo.class);
    // Verify the explicit (String-based) constructor was used
    assertEquals("foo", result.stringField);
    assertEquals(0, result.intField); // intField not set by String constructor
}
```

**Incorrect pattern to avoid:**
```java
// WRONG: Testing with a single constructor — won't trigger the overwrite bug
public class SimplePojo {
    @JsonCreator
    public SimplePojo(@JsonProperty("name") String name) { ... }
}
// This test would pass even on the buggy version.
```