---
name: creator-duplicate-resolution-guard
description: WHEN a class has a `verifyNonDup` method that returns boolean and decides
  whether a new creator should replace an existing one, THEN guard state mutation
  (`_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`) behind the boolean
  return value to avoid overwriting with invalid/rejected creators.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# creator-duplicate-resolution-guard

## Instructions

# Creator Duplicate Resolution Guarding

## Instructions

WHEN the test generator (TG) encounters code that resolves conflicts between multiple creator methods (constructors/factory methods) — specifically code that calls `verifyNonDup` and then unconditionally mutates state — THEN the TG should test that when a duplicate creator is rejected (non-explicit creator given an existing explicit one), the state (`_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`) is NOT updated.

Concretely:
- WHEN testing `addPropertyCreator(AnnotatedWithParams, boolean, SettableBeanProperty[])` or `addStringDelegate` / `addArrayDelegate` / similar creator registration methods
- THEN the TG should verify that when `verifyNonDup` returns `false` (the new creator is rejected), the corresponding state field (`_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`) retains its previous value
- Use the fixed version's pattern as the correct behavior: only assign `_propertyBasedArgs = properties` inside `if (verifyNonDup(...)) { ... }`, not unconditionally after it

The triggering test for this bug is: `com.fasterxml.jackson.databind.creators.Creator1476Test.testConstructorChoice`. The buggy version unconditionally assigned `_propertyBasedArgs = properties` after `verifyNonDup`, even when the new creator was rejected (e.g., an implicit creator tried to override an explicit one). This caused the properties array to be overwritten with a stale/wrong set of properties, leading to a `JsonMappingException: "Could not find creator property with name '...'"` on deserialization.

Common pitfalls:
- Testing only the "happy path" where `verifyNonDup` returns `true` and the new creator is accepted
- Not testing the rejection path where `verifyNonDup` returns `false` due to an existing explicit creator
- Testing only `addPropertyCreator` but not other creator registration methods that also guard state behind `verifyNonDup` (e.g., `addStringDelegate`, `addArrayDelegate`)
- Testing the wrong exception type — the bug manifests as `JsonMappingException` during deserialization, not an explicit exception at creator registration time

Example correct test:
```java
// Given a POJO with an explicit constructor and an implicit one
// When deserializing JSON matching the explicit constructor's parameters
// Then deserialization should succeed using the explicit creator's property names
ObjectMapper mapper = new ObjectMapper();
SimplePojo result = mapper.readValue("{\"intField\": 1, \"stringField\": \"foo\"}", SimplePojo.class);
assertEquals(1, result.intField);
assertEquals("foo", result.stringField);
```

Example incorrect test (would pass on buggy version too, missing the bug):
```java
// Only tests that a single creator works — doesn't test the conflict resolution
ObjectMapper mapper = new ObjectMapper();
SimplePojo result = mapper.readValue("{\"value\": 42}", SimplePojo.class);
assertEquals(42, result.value);
// This doesn't exercise the duplicate resolution code path at all
```

Key indicators that this skill applies:
- The class has a `verifyNonDup` method whose return type was changed from `void` to `boolean`
- State assignments (`_propertyBasedArgs = properties`, `_delegateArgs = ...`, `_arrayDelegateArgs = ...`) follow `verifyNonDup` calls
- The code has creator registration methods that accept both explicit and implicit flags