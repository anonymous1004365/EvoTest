---
name: token-store-put-state-validation
description: When testing methods that insert or update state in a store/repository,
  verify that putting the same data twice does not corrupt internal state. The TG
  should test that repeated putToken calls with the same data work consistently, catching
  cases where state is incorrectly tracked or validated.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STATE_MUTATION
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# token-store-put-state-validation

## Instructions

# Token Store Put State Validation

## Instructions

- WHEN the TG encounters a method that adds or updates data (e.g., `putToken(token)`) in a store, repository, or collection-based data structure
- THEN it should test the **idempotency** of the operation by calling the put method **twice with the same data** and verifying that both operations succeed without throwing exceptions or corrupting state
- Include tests that:
  1. First, put the data successfully
  2. Then, put the **same data again** (same key, same values)
  3. Verify that the second call does not throw any exception (such as `AssertionError`, `IllegalStateException`, or `IllegalArgumentException`)
  4. Verify that the state after the second put is still consistent (e.g., the data can be retrieved and matches expectations)
- Be careful to use the **exact same object** (or an equal object with same identifying fields) for both calls — not just structurally similar data
- Common pitfalls:
  - **Testing only the first insertion** without verifying re-insertion behavior — this misses bugs where internal maps/sets track state incorrectly
  - **Assuming the second put will fail with a specific exception** — the bug might cause a crash (e.g., `AssertionError`) or silently corrupt state; test for both success paths and state consistency
  - **Using distinct data for each call** — the bug only manifests when the **same** data is put a second time, not when putting different data

### Correct Example (catches the bug)
```java
// Test that putting the same token twice works
String token = createTestToken();
store.putToken(token);  // first insertion succeeds

// Second insertion of same token should also succeed
store.putToken(token);  // BUGGY version throws AssertionError here
```

### Incorrect Example (misses the bug)
```java
// Only testing single insertion — does not catch duplicate-put bug
String token = createTestToken();
store.putToken(token);  // passes on both buggy and fixed

// OR: Testing with different data each time
store.putToken("token1");
store.putToken("token2");  // different data, bug does not trigger
```