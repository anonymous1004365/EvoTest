---
name: creator-dedup-return-guard
description: When a creator collector method (like verifyNonDup) is called and its
  result determines whether state should be updated, the TG must test that a false
  return prevents state mutation. This skill catches bugs where verifyNonDup returns
  false but the caller unconditionally overwrites creator state.
code_tags:
- VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# creator-dedup-return-guard

## Instructions

# Creator Deduplication Return Guard

## Instructions

- WHEN the TG encounters a `verifyNonDup` (or similar deduplication) method that was changed from `void` to `boolean`, and its callers were updated to conditionally guard state assignments (e.g., `_delegateArgs`, `_arrayDelegateArgs`, `_propertyBasedArgs`)
- THEN the TG should write a test that verifies that when a more specific creator already exists, a subsequent less-specific creator does NOT overwrite the stored arguments. Specifically, test that:
  1. A creator is first registered (e.g., via `addPropertyCreator` or `addStringCreator` with `explicit=true`)
  2. A second, less specific/less explicit creator is then registered (e.g., via `addPropertyCreator` or `addStringCreator` with `explicit=false`)
  3. The state (e.g., `_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`) should still hold the values from the first (more specific) creator, NOT the second
  4. Verify this by attempting to deserialize JSON that matches the first creator's parameters and checking that deserialization succeeds
- WHEN testing this pattern, include the following concrete checks:
  - A POJO class with at least two constructors or factory methods, one explicitly annotated (e.g., `@JsonCreator`) and one not
  - The explicit constructor should have different parameter names/types than the implicit one
  - JSON input should match the explicit constructor's parameters
  - On the buggy version, deserialization should throw `JsonMappingException` because the implicit creator overwrote the explicit one's property metadata
  - On the fixed version, deserialization should succeed and produce the correct POJO
- Common pitfalls to avoid:
  - Testing only the happy path where a single creator exists — this misses the deduplication/overwrite bug entirely
  - Testing only with identical creator parameter types — the bug manifests when a more-explicit creator is followed by a less-explicit one with different parameters
  - Assuming `verifyNonDup` is only about duplicate detection — it also decides WHICH creator wins, and its return value controls state mutation
  - Not testing that the state (`_propertyBasedArgs`, `_delegateArgs`, etc.) is correctly guarded — verify this via integration (deserialization) rather than direct state inspection

**Correct test approach:**
```java
// POJO with @JsonCreator on one constructor
static class SimplePojo {
    int intField;
    String stringField;
    
    @JsonCreator
    public SimplePojo(@JsonProperty("intField") int intField, 
                      @JsonProperty("stringField") String stringField) {
        this.intField = intField;
        this.stringField = stringField;
    }
    
    // Implicit constructor (no annotation) — should NOT override the explicit one
    public SimplePojo(String dummy) {
        this.stringField = dummy;
    }
}

// Test: deserialize using explicit creator's parameters
ObjectMapper mapper = new ObjectMapper();
SimplePojo result = mapper.readValue("{\"intField\": 1, \"stringField\": \"foo\"}", SimplePojo.class);
assertEquals(1, result.intField);
assertEquals("foo", result.stringField);
```

**Incorrect test approach (misses the bug):**
```java
// Only testing with a single creator — no deduplication scenario
static class SimplePojo {
    @JsonCreator
    public SimplePojo(@JsonProperty("value") int value) { ... }
}
// This would pass on both buggy and fixed versions, not catching the overwrite bug
```