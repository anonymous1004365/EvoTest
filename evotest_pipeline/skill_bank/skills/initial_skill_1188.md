---
name: creator-duplicate-verification-guard
description: When collecting bean creators with explicit annotations, verifyNonDup
  may indicate a more specific creator already exists and the new one should be skipped
  — guard assignments behind the boolean return value instead of blindly overwriting.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# creator-duplicate-verification-guard

## Instructions

# Creator Duplicate Verification Guard

## Instructions

- WHEN the TG encounters a class that collects multiple alternative creators (constructors/factory methods) for a bean, where a `verifyNonDup` (or similar deduplication) method compares creator types and decides which one to use
- THEN the TG should test scenarios where:
  1. An explicitly annotated creator (e.g. `@JsonCreator`) is defined alongside a non-annotated creator
  2. The non-annotated creator's parameter type is more specific (less generic) than the explicit one's parameter type
  3. The system should correctly use the explicit creator, NOT silently overwrite it with the non-annotated one
  
- The TG should verify that when a creator with an explicit annotation already exists, attempting to add another creator via methods like `addPropertyCreator`, `addStringDelegateCreator`, or `addArrayDelegateCreator` does NOT overwrite the existing creator's configuration (e.g. `_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`).
- The test should construct two candidate creators — one with explicit annotation and one without — where the non-explicit one would be "more specific" in type, and verify that deserialization still uses the explicit creator's properties correctly (expect SUCCESS, not `JsonMappingException` about missing properties).
- Common pitfalls to avoid:
  - Testing only the case where one creator exists — must test the **interaction** between multiple candidates
  - Forgetting that `verifyNonDup` previously returned `void` and unconditionally assigned fields — the fix makes it return `boolean` and only assigns when the new creator is accepted
  - Testing only same-type duplicates — the critical case is when the non-explicit creator has a **more specific parameter type** (e.g., `String` vs `Object`), causing it to be preferred erroneously
  - Not verifying that the EXPLICIT creator's properties are the ones that take effect after deserialization

**Correct example** (tests a scenario with explicit annotation + non-explicit more-specific creator):
```java
public void testConstructorChoice() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    // SimplePojo has an explicit @JsonCreator constructor with two properties
    // and a non-explicit constructor with a single String parameter
    SimplePojo result = mapper.readValue("{\"intField\":1,\"stringField\":\"foo\"}", SimplePojo.class);
    assertEquals(1, result.intField);
    assertEquals("foo", result.stringField);
}
```

**Incorrect approach** (only tests a single creator path):
```java
public void testSingleCreator() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    // Only one creator exists — doesn't test the conflict case
    Foo result = mapper.readValue("{\"a\":1}", Foo.class);
    assertNotNull(result);
}
```