---
name: creator-collector-override-validation
description: When overriding creator results (like constructors) in a `CreatorCollector`,
  the TG should test that invalid overrides (e.g., mismatched parameter types) do
  NOT silently replace valid creators, but instead either merge properly or throw
  an appropriate exception. This skill applies to deserialization creator logic in
  Jackson.
code_tags:
- STATE_MUTATION
- ARGUMENT_VALIDATION
- CREATOR_DEDUP_OVERRIDE
test_pattern: STATE_TEST
---

# creator-collector-override-validation

## Instructions

# Creator Collector Override Validation

## Instructions

- WHEN the TG encounters code that collects or merges creator results (constructors, factory methods) in a `CreatorCollector` or similar aggregator, and a new creator with the same name/position can override or replace an existing one:
  - THEN the TG should write a test that exercises the code path where a creator with mismatched parameter types (e.g., `String` vs `CtTypeReference`) is added, and verify that the invalid override does NOT silently replace the valid creator. The test should verify that the final set of creators still contains the originally valid creator (e.g., by checking that deserialization uses the correct creator).
  - Include concrete values: use `CreatorCollector` directly (or through `DeserializationConfig`/`ObjectMapper`), add creators with different parameter types, and assert that overriding does not corrupt the creator state.
  - Common pitfalls: testing only a single-type parameter (e.g., only `String` types), or testing only the happy path where override is consistent. The TG must also test the case where the parameter types differ between the existing creator and the replacing creator, and verify that the state remains correct.

## Examples

### Correct (catches the bug):
```java
// Given a CreatorCollector that already has a creator for "creatorName" with
// a String parameter type, adding another creator for the same property name
// with a different parameter type (e.g., CtTypeReference) should NOT
// silently replace the existing creator.
CreatorCollector collectors = new CreatorCollector(...);
// ... setup existing creator with String param type ...
// ... attempt invalid override with different param type ...
assertNotNull("Original creator should still be present", 
    collectors.findCreator("creatorName"));
// The type of the creator parameter should still be the original type
```

### Incorrect (does not catch the bug):
```java
// Only testing with consistent parameter types
CreatorCollector collectors = new CreatorCollector(...);
// ... both creators use String param type ...
// This would not catch a bug where type mismatch causes silent override
```