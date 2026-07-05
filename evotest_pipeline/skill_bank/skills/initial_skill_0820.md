---
name: creator-collector-verify-nondup-guard
description: When a method previously returned void and was changed to return boolean (indicating whether to use a creator), callers that blindly assign state after the call may corrupt internal state. Tests must verify both the assigned and rejected scenarios using creator overloads with different parameter sets.
code_tags: ['TYPE_CONVERSION', 'VALIDATION']
test_pattern: STATE_TEST
---

# creator-collector-verify-nondup-guard

## Instructions

# Creator Collector verifyNonDup Guard

## Instructions

- WHEN the TG encounters a `CreatorCollector`-like class where `verifyNonDup(...)` changes from `void` to `boolean` (returning `true` when the new creator is to be used, `false` when it is rejected in favor of an existing one), and the callers unconditionally assign internal fields (like `_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`) after calling `verifyNonDup(...)`
- THEN the TG should write a test that provides TWO different constructors/creators (e.g., one explicit, one implicit) for the SAME type index so that `verifyNonDup(...)` returns `false` (rejecting the second one), and verify that the rejected creator's associated internal field (`_propertyBasedArgs`, `_delegateArgs`, `_arrayDelegateArgs`) is **NOT** overwritten — specifically, that the first creator's properties are retained instead of being replaced with `null` or the second creator's properties
- Concrete example: In `CreatorCollector`, calling `addPropertyCreator(creator1, true, props1)` then `addPropertyCreator(creator2, false, props2)` — where `creator2` is rejected because `creator1` was explicit — must NOT set `_propertyBasedArgs` to `props2` or `null`; it must keep `props1`. Similarly, `addStringCreator` with a delegating creator followed by another with a more generic type must not overwrite `_delegateArgs`.
- The test must verify the **state** of the internal storage field after the second (rejected) call, e.g. by deserializing a JSON input that triggers the creator resolution and asserting that no `JsonMappingException` about missing creator properties occurs.
- Common pitfalls:
  - Testing only the case where the second creator is accepted (both calls with the same explicitness level), missing the rejection case
  - Only testing `addPropertyCreator` but not `addStringCreator` / `addDelegatingCreator` which have the same bug pattern with `_delegateArgs` / `_arrayDelegateArgs`
  - Forgetting that the bug manifests as a `JsonMappingException` at deserialization time because `_propertyBasedArgs` gets overwritten with `null`
  - Testing with `verifyNonDup` returning `true` (success path) rather than `false` (rejection path)

### Correct example

```java
// Test that when addPropertyCreator is called with an explicit creator first,
// then with an implicit (non-explicit) creator second, the implicit one is rejected
// and the internal _propertyBasedArgs retains the first creator's properties.
// Without the fix, this would clear _propertyBasedArgs and cause a deserialization error.
ObjectMapper mapper = new ObjectMapper();
// SimplePojo has two constructors: one annotated @JsonCreator (explicit), one not
SimplePojo result = mapper.readValue("{\"intField\":1,\"stringField\":\"foo\"}", SimplePojo.class);
assertEquals(1, result.intField);
assertEquals("foo", result.stringField);
```

### Incorrect example

```java
// BAD: Only tests the happy path where the second creator is also explicit,
// missing the bug scenario where an implicit creator overwrites an explicit one's properties.
ObjectMapper mapper = new ObjectMapper();
SimplePojo result = mapper.readValue("{\"intField\":1}", SimplePojo.class);
assertNotNull(result);
// This test passes on both buggy and fixed versions, giving false confidence.
```