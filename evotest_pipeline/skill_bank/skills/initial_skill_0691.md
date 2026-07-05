---
name: disable-branch-state-validation
description: When a code path disables a feature (e.g., branches) via configuration/mutable
  state, the test generator should verify that concurrent operations no longer attempt
  to use the disabled feature. This applies when state mutation controls feature gating
  and the validation of that gating is absent or incomplete.
code_tags:
- STATE_MUTATION
- ARGUMENT_VALIDATION
- BACKGROUND_THREAD_LEASE_UPDATE
test_pattern: STATE_TEST
---

# disable-branch-state-validation

## Instructions

# Disable Branch State Validation

## Instructions

- WHEN the TG encounters code that modifies a configuration value or system state to disable a feature (e.g., setting `disableBranches = true` on `DocumentNodeStore`), and the code has operations that check this configuration before performing feature-specific work (e.g., branch creation)
- THEN the TG should write a test that:
  1. Creates an instance of the component that manages the feature (e.g., `DocumentNodeStore`)
  2. Calls the setter/method that disables the feature (e.g., `store.setDisableBranches(true)`)
  3. After disabling, executes the operation(s) that should skip the disabled feature (e.g., `store.backgroundWrite()`)
  4. Asserts that the operation does NOT attempt to use the disabled feature — for example, by verifying no `IllegalStateException` is thrown or that no `Branch` objects are created when they shouldn't be
  5. Additionally, verify the operation completes successfully (returns without error) after the feature is disabled
- Common pitfalls to avoid:
  - Testing only the "happy path" where the feature is enabled (default) and missing the disabled-state path entirely
  - Forgetting to reset state between test runs — ensure the feature is actively set to disabled within the test, not relying on defaults
  - Testing only the setter value (e.g., `assertTrue(store.isDisableBranches())`) without testing that the downstream behavior actually respects the disabled state
  - Assuming that if a feature is disabled, skip logic exists — the bug is precisely when skip logic is missing

### Correct Example (what the TG should produce)

```java
@Test
public void backgroundWriteWithDisabledBranches() {
    DocumentNodeStore store = new DocumentNodeStore(...);
    store.setDisableBranches(true);  // disable branches
    
    // This should NOT throw or create branches when disableBranches==true
    store.backgroundWrite();
    
    // Verify no branch-related state was created
    assertTrue(store.getBranches().isEmpty());
}
```

### Incorrect Example (common pitfalls)

```java
@Test
public void testDisableBranchesSetter() {
    DocumentNodeStore store = new DocumentNodeStore(...);
    store.setDisableBranches(true);
    // Only testing the setter, not the downstream behavior!
    assertTrue(store.isDisableBranches());
}
```