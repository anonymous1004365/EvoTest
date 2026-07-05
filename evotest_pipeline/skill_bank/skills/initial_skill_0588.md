---
name: creator-registration-guard-verification
description: WHEN registering constructors/factory methods as JSON creators (delegating,
  property-based, array-delegating), THEN test that when a creator is rejected by
  verifyNonDup (e.g., a more specific creator already exists), its associated injectables/properties
  are NOT registered, preventing silent overwrite of the correct creator's configuration.
code_tags:
- TYPE_CONVERSION
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# creator-registration-guard-verification

## Instructions

# Creator Registration Guard Verification

## Instructions

WHEN the TG encounters a `CreatorCollector` class (or similar) that:
1. Calls a method like `verifyNonDup(creator, typeIndex, explicit)` **before** assigning `_delegateArgs`, `_arrayDelegateArgs`, `_propertyBasedArgs`, or similar fields.
2. The buggy version **ignores the return value** of `verifyNonDup` and proceeds with the assignment unconditionally.

THEN the TG should write a test that:
- Creates two conflicting creator candidates (e.g., a `@JsonCreator` annotated constructor and a non-annotated constructor) where the second creator should be **rejected** by the deduplication logic.
- Verifies that after the second (rejected) creator is processed, the `_delegateArgs` / `_propertyBasedArgs` / `_arrayDelegateArgs` fields have **NOT been overwritten** and still hold the values from the first (accepted) creator.
- Specifically, simulate the scenario where `verifyNonDup` returns `false` (e.g., the existing creator is explicit and the new one is not), and confirm the field assignment is skipped.
- Use reflection or test helper methods if the fields are private, or test via the public behavior (e.g., deserialization with conflicting `@JsonCreator` methods).

**Common pitfalls to avoid:**
- Only testing the happy path (one creator) without testing the **rejection path** where a second creator is silently accepted.
- Assuming that if `verifyNonDup` is called, the assignment is automatically guarded — must check the actual field value after the call.
- Testing with only `@JsonCreator`-annotated methods; also test with **mixed** scenarios (one explicit, one implicit) to trigger the `boolean explicit` comparison.
- Confusing the old buggy behavior (unconditional assignment) with the fixed behavior (guarded by `verifyNonDup` return value).

**Correct test example:**
```java
// Given: Two conflicting constructors where the second should be rejected
AnnotatedWithParams firstCreator = ...; // explicit @JsonCreator
AnnotatedWithParams secondCreator = ...; // no annotation, should be rejected

// When: Both are registered
creatorCollector.addPropertyCreator(firstCreator, true, props1);
creatorCollector.addPropertyCreator(secondCreator, false, props2);

// Then: The second props2 should NOT overwrite the first props1
// (verify via the actual deserialization behavior or via reflection)
assertNotNull(creatorCollector._propertyBasedArgs); // still set from first
// The exact assertion depends on the exposed API
```

**Incorrect test example (what NOT to do):**
```java
// Only testing a single creator registration — misses the bug entirely
AnnotatedWithParams creator = ...;
creatorCollector.addPropertyCreator(creator, true, props);

// This passes even on the buggy version because there's no conflict
assertNotNull(creatorCollector._propertyBasedArgs);
```