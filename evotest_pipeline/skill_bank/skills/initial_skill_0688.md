---
name: creator-collector-duplicate-registration-guard
description: When testing creator registration in Jackson's CreatorCollector, test
  that when multiple constructors/factory methods exist, the verifyNonDup method correctly
  guards against overriding previously registered explicit creators, especially when
  the new creator is less specific or not explicitly annotated.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
- DUPLICATE_CREATOR_REGISTRATION
test_pattern: EXCEPTION_TEST
---

# creator-collector-duplicate-registration-guard

## Instructions

# Creator Registration Duplicate Guard Test

## Instructions

- WHEN the TG encounters a method that registers creators (e.g., `addPropertyCreator`, `addStringCreator`, `addDelegatingCreator`) and deduplication logic exists via `verifyNonDup` with state fields like `_creators[]`, `_hasNonDefaultCreator`, and `_explicitCreators` mask
- THEN the TG should test the scenario where multiple creators exist for the same property and verify that:
  1. An **explicit** creator (e.g., annotated with `@JsonCreator`) should **win over** a non-explicit (implicit) creator for the same property type
  2. A **more specific** type creator should win over a less specific one (e.g., `String` vs `Object` parameter)
  3. When a subsequent creator is **rejected** (returns `false` from `verifyNonDup`), the previously registered creator's arguments (`_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`) should **not** be overwritten
  4. When an explicit creator is registered first, a second non-explicit creator for the same type should not replace the first — and the test should verify that deserialization still works using the first (more explicit/specific) creator

- Include tests that:
  - Define a POJO with multiple constructors: one explicit `@JsonCreator` constructor and one implicit default constructor
  - Register the implicit creator first, then the explicit creator
  - Verify that deserialization of JSON produces the object using the explicit creator (not losing property bindings)
  - Expect that the explicit creator's property bindings remain intact (i.e., deserialization does NOT throw `JsonMappingException` saying "Could not find creator property with name '...'")

- Common pitfalls to avoid:
  - Testing only a single creator registration without verifying what happens when a second creator is registered for the same property
  - Assuming that simply calling `verifyNonDup` is sufficient — the bug is that the old code ALWAYS overwrote creator arguments even when the new creator was rejected
  - Not testing the scenario where an implicit (non-`@JsonCreator`) constructor is registered before an explicit one — the bug only manifests when the implicit one overrides the explicit one's property args
  - Testing registration in isolation without testing that the **registered creator is actually used** during deserialization

- Example correct test pattern:
```java
// POJO with two constructors
static class SimplePojo {
    int intField;
    String stringField;
    
    @JsonCreator
    public SimplePojo(@JsonProperty("intField") int intField, 
                      @JsonProperty("stringField") String stringField) {
        this.intField = intField;
        this.stringField = stringField;
    }
    
    // Implicit constructor - should NOT override the explicit one
    public SimplePojo() { }
}

@Test
public void testExplicitCreatorTakesPrecedence() {
    ObjectMapper mapper = new ObjectMapper();
    // This should succeed: explicit @JsonCreator constructor should be used
    SimplePojo result = mapper.readValue(
        "{\"intField\": 1, \"stringField\": \"foo\"}", 
        SimplePojo.class
    );
    assertEquals(1, result.intField);
    assertEquals("foo", result.stringField);
}
```

- Example incorrect test (would NOT catch the bug):
```java
// Tests only a single creator - misses the duplicate registration bug
@Test
public void testPropertyCreatorRegistration() {
    // Only tests a single creator, no duplicate scenario
    ObjectMapper mapper = new ObjectMapper();
    SimplePojo result = mapper.readValue("{\"intField\": 1}", SimplePojo.class);
    assertEquals(1, result.intField);
}
```