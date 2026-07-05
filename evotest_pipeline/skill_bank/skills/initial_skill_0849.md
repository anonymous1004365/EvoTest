---
name: creator-duplicate-overwrite-check
description: When a class has multiple constructors/factory methods (creators), the
  code may overwrite a previously registered creator with a new one without proper
  deduplication checks, causing property-based constructors to be lost and deserialization
  to fail. Tests should verify that when an explicit property-based creator exists
  alongside delegate creators, the property-based creator is correctly selected.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- EMPTY_COLLECTION_HANDLING
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# creator-duplicate-overwrite-check

## Instructions

# Creator Duplicate Overwrite Check

## Instructions

- WHEN the TG encounters a method that registers creators (constructors/factory methods) where a `verifyNonDup` method is called but its result/return value is ignored, and `_propertyBasedArgs`, `_delegateArgs`, or `_arrayDelegateArgs` fields are unconditionally overwritten after the call
- THEN the TG should write a test that creates a POJO with **both** a single-argument delegate constructor (e.g., taking `Collection`, `Map`, or `String`) AND a multi-argument property-based constructor annotated with `@JsonCreator` and `@JsonProperty` annotations, then attempts to deserialize JSON that matches the property-based constructor (e.g., `{"intField": 1, "stringField": "foo"}`)
  - The test should verify that deserialization succeeds and produces an object with the correct field values
  - On the buggy version, the expected behavior is that deserialization throws a `com.fasterxml.jackson.databind.JsonMappingException` with a message containing "Could not find creator property with name ..."
  - On the fixed version, deserialization produces the correctly populated POJO

- Common pitfalls to avoid:
  - Testing only one creator type at a time (e.g., only delegate or only property-based) — this will not reveal the bug
  - Forgetting to make both constructors discoverable via annotations — the property-based constructor needs `@JsonCreator` + `@JsonProperty` on each parameter, the delegate constructor needs `@JsonCreator` with a single unannotated parameter
  - Assuming that the order of constructor definitions in the source code determines selection priority — the bug is about the `verifyNonDup` method returning `void` instead of `boolean`, causing unconditional overwrite regardless of priority
  - Testing with only String-type parameters — the bug affects all property types including primitive `int`, `long`, `boolean`, etc.

### Example (correct test pattern):

```java
// POJO with two constructors — one delegate, one property-based
static class SimplePojo {
    private int intField;
    private String stringField;
    
    // Delegate constructor (would be selected incorrectly in buggy version)
    @JsonCreator
    public SimplePojo(String value) {
        this.intField = 0;
        this.stringField = value;
    }
    
    // Property-based constructor (should be selected)
    @JsonCreator
    public SimplePojo(@JsonProperty("intField") int intField,
                      @JsonProperty("stringField") String stringField) {
        this.intField = intField;
        this.stringField = stringField;
    }
}

@Test
public void testConstructorChoice() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    // This should use the property-based constructor
    SimplePojo result = mapper.readValue(
        "{\"intField\": 1, \"stringField\": \"foo\"}", SimplePojo.class);
    assertEquals(1, result.intField);
    assertEquals("foo", result.stringField);
}
```

### Example (incorrect test — won't catch the bug):

```java
// BAD: Only testing delegate constructor — won't reveal the overwrite bug
@Test
public void testDelegateOnly() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    SimplePojo result = mapper.readValue("\"test\"", SimplePojo.class);
    assertEquals("test", result.stringField);
}
```