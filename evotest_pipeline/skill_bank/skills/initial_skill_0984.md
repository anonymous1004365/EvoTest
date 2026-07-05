---
name: creator-overwrite-defensive-gate
description: When a method overwrites internal state (like _arrayDelegateArgs, _delegateArgs,
  or _propertyBasedArgs) after calling a verification method like verifyNonDup, the
  TG should test that state is NOT overwritten when the verification method indicates
  the new creator should be rejected (returns false).
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# creator-overwrite-defensive-gate

## Instructions

# Creator Overwrite Defensive Gate

## Instructions

- WHEN the TG encounters a method (e.g., `addStringCreator`, `addDelegatingCreator`, `addPropertyCreator`) in a creator collector class (like `CreatorCollector`) that:
  1. Calls a verification method (e.g., `verifyNonDup`) BEFORE overwriting internal state fields (e.g., `_arrayDelegateArgs`, `_delegateArgs`, `_propertyBasedArgs`)
  2. The verification method has been changed from `void` return to `boolean` return — where `false` means "skip this creator"
  
- THEN the TG should write a test that verifies:
  - When `verifyNonDup` returns `false` (meaning the new creator is rejected), the internal state fields (`_arrayDelegateArgs`, `_delegateArgs`, `_propertyBasedArgs`) are NOT overwritten with new values
  - Specifically, provide two creators in sequence: first a more-specific creator (which gets accepted), then a less-specific creator (which gets rejected via `verifyNonDup` returning `false`), and assert that the second call does NOT wipe out the first creator's state

- WHEN the code has `addIncompleteParameter` or similar methods that add to a collection (like `_incompleteParameters` in `CreatorCollector`)
- THEN the TG should test that adding an incomplete parameter to a non-null list does NOT cause a `NullPointerException` when the parameter's type is `Void.TYPE` or similar primitive type wrapper

- Common pitfalls to avoid:
  - Do NOT assume `verifyNonDup` always succeeds — it can return `false` when a more specific creator already exists
  - Do NOT test only the happy path where a single creator is registered
  - Do NOT forget to test the SPECIFIC scenario where a method like `addPropertyCreator` is called with one creator first (more specific type), and then again with another creator (less specific type), and verify the second call doesn't overwrite properties set by the first
  - Do NOT write tests that only check `verifyNonDup` returns a boolean — verify the ACTUAL state mutation consequences (which internal fields got set)

### Correct Example

```java
// Test that addPropertyCreator does NOT overwrite _propertyBasedArgs when
// verifyNonDup returns false (rejecting a less-specific creator)

// Given a CreatorCollector with an initial property creator registered
CreatorCollector collector = new CreatorCollector(...);
AnnotatedWithParams firstCreator = ...; // e.g., a constructor with specific type
SettableBeanProperty[] firstProps = ...;
collector.addPropertyCreator(firstCreator, true, firstProps);

// When a second, less-specific creator is added (should be rejected)
AnnotatedWithParams secondCreator = ...; // e.g., a constructor with more generic type
SettableBeanProperty[] secondProps = ...;
collector.addPropertyCreator(secondCreator, false, secondProps);

// Then the original _propertyBasedArgs should still be the first creator's props
// NOT overwritten by the second call
// (This would fail on buggy versions where _propertyBasedArgs = properties; was set unconditionally)
assertNotNull(collector.getPropertyBasedArgs());
assertEquals(firstProps.length, collector.getPropertyBasedArgs().length);
```

### Incorrect Example

```java
// BAD: Only testing the happy path — single creator registration
CreatorCollector collector = new CreatorCollector(...);
AnnotatedWithParams creator = ...;
SettableBeanProperty[] props = ...;
collector.addPropertyCreator(creator, true, props);
// This would pass on both buggy and fixed versions — useless!
assertNotNull(collector.getPropertyBasedArgs());

// BAD: Only testing that verifyNonDup returns a value without checking state
// This doesn't catch the state mutation bug
```