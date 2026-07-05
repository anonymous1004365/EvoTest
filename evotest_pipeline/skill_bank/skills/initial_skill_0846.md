---
name: creator-override-selection-logic
description: When multiple constructors or factory methods exist for deserialization,
  the creator selection logic may incorrectly overwrite the chosen creator. Apply
  this skill when testing Jackson creator-based deserialization where a class has
  multiple constructors (parameterized and default) or factory methods.
code_tags:
- NULL_CHECK
- VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# creator-override-selection-logic

## Instructions

# Creator Override Selection Logic in Jackson Deserialization

## Instructions

WHEN the TG encounters code that involves Jackson deserialization where a Java class has **multiple constructors** (e.g., a parameterized constructor with `@JsonCreator` and a default no-arg constructor, or multiple `@JsonCreator`-annotated constructors/factory methods),

THEN the TG MUST write a parametric test that:

1. **Verifies that deserialization correctly selects the annotated creator when a non-annotated constructor also exists.** In the buggy version, the `verifyNonDup` method returned `void` and the caller unconditionally assigned `_propertyBasedArgs = properties` even when `verifyNonDup` determined the new creator should be discarded (e.g., when a non-explicit creator tried to override an explicit one). The fix changed `verifyNonDup` to return `boolean` and only assign the properties when it returns `true`.

2. **Test with a class that has BOTH:**
   - A parameterized constructor annotated with `@JsonCreator` (explicit creator)
   - A default no-arg constructor (implicit creator)

3. **Verify that deserializing JSON into this class:**
   - Succeeds without throwing `JsonMappingException`
   - Correctly populates all fields from the JSON input
   - The error message "Could not find creator property with name '...'" should NOT appear

4. **Use `ObjectMapper` to perform deserialization** and assert the result is correctly populated.

5. **Common pitfalls to avoid:**
   - ❌ Testing only a class with a single constructor (single-creator cases don't trigger the bug)
   - ❌ Testing only deserialization failure cases without checking that the result is correct
   - ❌ Using a class with `@JsonCreator` on a factory method but forgetting that the bug also applies to constructor-based creators
   - ❌ Assuming that because there's no compilation error, deserialization will work at runtime

**Correct example:**

```java
// Class under test
static class SimplePojo {
    int intField;
    String stringField;
    
    // Default constructor — implicit creator
    public SimplePojo() { }
    
    // Annotated constructor — explicit creator
    @JsonCreator
    public SimplePojo(@JsonProperty("intField") int intField, 
                      @JsonProperty("stringField") String stringField) {
        this.intField = intField;
        this.stringField = stringField;
    }
}

// Parametric test
@Test
public void testConstructorChoice() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    // This should deserialize correctly using the @JsonCreator constructor
    SimplePojo result = mapper.readValue(
        "{ \"intField\": 1, \"stringField\": \"foo\" }", 
        SimplePojo.class
    );
    assertEquals(1, result.intField);
    assertEquals("foo", result.stringField);
}
```

**Incorrect example (would not catch the bug):**

```java
// ❌ Only testing a single constructor — no override conflict
static class SingleConstructorPojo {
    int value;
    @JsonCreator
    public SingleConstructorPojo(@JsonProperty("value") int value) {
        this.value = value;
    }
}

// ❌ Testing failure mode only, not verifying correct population
@Test(expected = Exception.class)
public void testDeserialization() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    mapper.readValue("{}", SingleConstructorPojo.class);
}
```