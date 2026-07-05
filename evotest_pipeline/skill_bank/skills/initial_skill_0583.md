---
name: creator-overwrite-on-verify-nondup
description: When overwriting creators in Jackson's CreatorCollector, verifyNonDup
  should return a boolean to indicate whether the new creator should replace the old
  one. Always check the return value before assigning _delegateArgs, _arrayDelegateArgs,
  or _propertyBasedArgs.
code_tags:
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# creator-overwrite-on-verify-nondup

## Instructions

# Creator Overwrite on verifyNonDup Return Value

## Instructions

- WHEN the TG encounters code that calls a `verifyNonDup(creator, typeIndex, explicit)` method which previously returned `void` but now returns `boolean`:
  - THEN the TG should verify that the call site checks the **return value** before proceeding to overwrite fields like `_delegateArgs`, `_arrayDelegateArgs`, or `_propertyBasedArgs`.
  - Specifically, the TG should assert that if `verifyNonDup` returns `false` (indicating the old creator should be kept), then the corresponding field (`_delegateArgs`, `_arrayDelegateArgs`, `_propertyBasedArgs`) is **NOT** overwritten with the new values.
  - The TG should write a test that:
    1. Calls `addDelegatingCreator` or `addPropertyCreator` twice with creators of different priority (e.g., explicit vs non-explicit).
    2. Asserts that after the second call, the field still contains the value from the first (higher-priority) creator.
    3. On the buggy version, the field will be incorrectly overwritten; on the fixed version, the field retains the original value.

- Common pitfalls:
  - Assuming that just because `verifyNonDup` is called before assignment, the assignment is conditional on it. The bug was that the assignments (`_arrayDelegateArgs = ...`, `_delegateArgs = ...`, `_propertyBasedArgs = ...`) happened *unconditionally* after `verifyNonDup`, even when `verifyNonDup` decided to keep the old creator.
  - Testing only the happy path (single creator registration) — the bug only manifests when two creators compete and the second one should be rejected.

- **Incorrect test** (would not catch the bug):
  ```java
  // Only tests single creator — no overwrite scenario
  addDelegatingCreator(creator1, true, injectables1);
  assertEquals(injectables1, _arrayDelegateArgs);
  ```

- **Correct test** (catches the bug):
  ```java
  // Registers explicit creator first, then non-explicit — second should NOT overwrite
  addDelegatingCreator(explicitCreator, true, explicitInjectables);
  addDelegatingCreator(nonExplicitCreator, false, nonExplicitInjectables);
  // The buggy version would set _arrayDelegateArgs to nonExplicitInjectables
  // The fixed version keeps explicitInjectables
  assertEquals(explicitInjectables, creatorCollector.getArrayDelegateArgs());

  // Similarly for property creators
  addPropertyCreator(explicitPropertyCreator, true, explicitProperties);
  addPropertyCreator(nonExplicitPropertyCreator, false, nonExplicitProperties);
  assertEquals(explicitProperties, creatorCollector.getPropertyBasedArgs());
  ```