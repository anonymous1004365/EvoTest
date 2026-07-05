---
name: creator-dedup-return-value-check
description: WHEN verifying duplicate creator methods (constructors/factories) in
  deserialization, THEN test that the verification method's return value controls
  whether the creator is registered. This prevents later creators from overwriting
  earlier ones incorrectly.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# creator-dedup-return-value-check

## Instructions

# Creator Dedup Return Value Check

## Instructions

WHEN the TG encounters a method that calls `verifyNonDup` or similar deduplication logic for creator methods (constructors, factory methods, delegate creators, property creators) and then unconditionally stores/overwrites the creator arguments (`_delegateArgs`, `_arrayDelegateArgs`, `_propertyBasedArgs`), THEN the TG should test that the return value of `verifyNonDup` method is properly used to conditionally register the creator.

Specifically:
- WHEN a method like `addStringDelegateCreator`, `addPropertyCreator`, or `addDelegatingCreator` calls `verifyNonDup(creator, typeIndex, explicit)` and then unconditionally assigns `_delegateArgs = injectables` or `_propertyBasedArgs = properties`
- THEN the TG should verify that if `verifyNonDup` returns `false` (indicating the new creator should be skipped due to a conflict), the corresponding `_delegateArgs` / `_propertyBasedArgs` field should NOT be overwritten
- The test should create multiple conflicting creator definitions (e.g., two constructors annotated as `@JsonCreator`) where one is more specific or explicitly marked, and verify:
  1. The correct creator is chosen (the more specific or explicitly annotated one)
  2. The existing creator's properties/arguments are preserved, not replaced
  3. Deserialization succeeds and uses the intended creator

Common pitfalls:
- Testing only that `verifyNonDup` is called, without checking that its return value gates the field assignment
- Assuming that unconditional assignment is safe because `verifyNonDup` throws an exception on conflict (it doesn't — it returns `false` to skip)
- Testing with only a single creator, which won't exercise the dedup path at all
- Not testing with mixed explicit/implicit annotations, where an explicit annotation should win

Example correct test:
```java
// Both constructors annotated with @JsonCreator — explicit vs explicit conflict
// verifyNonDup should return true for one, false for the other
@JsonCreator
public SimplePojo(@JsonProperty("intField") int intField, 
                  @JsonProperty("stringField") String stringField) {
    this.intField = intField;
    this.stringField = stringField;
}

@JsonCreator
public SimplePojo(@JsonProperty("intField") int intField) {
    this.intField = intField;
    this.stringField = "default";
}

// Deserialization should use the 2-arg constructor (correct)
// NOT the 1-arg constructor overwriting the stored creator
String json = "{\"intField\": 1, \"stringField\": \"foo\"}";
SimplePojo result = mapper.readValue(json, SimplePojo.class);
assertEquals(1, result.intField);
assertEquals("foo", result.stringField); // This would fail if 1-arg constructor overwrites
```

Example incorrect test (doesn't detect the bug):
```java
// Only single creator — no dedup conflict exercised
@JsonCreator
public SimplePojo(@JsonProperty("intField") int intField,
                  @JsonProperty("stringField") String stringField) { ... }

String json = "{\"intField\": 1, \"stringField\": \"foo\"}";
SimplePojo result = mapper.readValue(json, SimplePojo.class);
// This passes even with the buggy code since no conflict occurs
```