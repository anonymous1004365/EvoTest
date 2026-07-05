---
name: thread-context-map-filter-single-key-npe
description: When testing a ThreadContextMapFilter configured with a single key/value
  pair (useMap=false), the filter() method directly calls value.equals(currentContextData().getValue(key))
  which throws NullPointerException if the context value is null. Tests must verify
  both matching and non-matching context values, including when the context key is
  absent entirely.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# thread-context-map-filter-single-key-npe

## Instructions

# ThreadContextMapFilter Single Key NullPointerException

## Instructions

WHEN testing `ThreadContextMapFilter` created via `ThreadContextMapFilter.createFilter()` with a **single** `KeyValuePair` (e.g., `new KeyValuePair("userid", "testuser")`):

- THEN configure the filter with a single key-value pair where the value list has exactly one element, so that `useMap` is set to `false` and the fast-path `filter()` method is exercised.
- THEN ensure the test covers these cases:
  1. The matching thread context key has a matching value — should return `Result.NEUTRAL` (or `onMatch`).
  2. The matching thread context key has a **non-matching** value — should return `Result.DENY` (or `onMismatch`).
  3. The matching thread context key is **absent** (not set or removed via `ThreadContext.remove()`) — the buggy code throws `NullPointerException` because `value.equals(currentContextData().getValue(key))` calls `.equals()` on a null return from `getValue()`. The test must expect `Result.DENY` (or `onMismatch`) in this case on the fixed version; on the buggy version, this will throw NPE.
- WHEN the filter is configured with **multiple** key-value pairs (so `useMap=true`): THEN test the same scenarios since the `useMap=true` path iterates the map and also calls `currentContextData.getValue(...)` which can return null.
- Mistake to avoid: Only testing with the matching value present, and forgetting to test when the context key is missing from ThreadContext entirely (e.g., after `ThreadContext.clearMap()` or `ThreadContext.remove("key")`).

### Example (correct — tests all cases including missing key):

```java
@Test
public void testFilterSinglePairWithMissingKey() {
    // Single pair filter: userid=testuser
    KeyValuePair[] pairs = new KeyValuePair[] { new KeyValuePair("userid", "testuser") };
    ThreadContextMapFilter filter = ThreadContextMapFilter.createFilter(pairs, null, null, null);
    filter.start();

    // Case 1: key present, value matches
    ThreadContext.put("userid", "testuser");
    assertSame(Filter.Result.NEUTRAL, filter.filter(null, Level.DEBUG, null, (Object) null, (Throwable) null));

    // Case 2: key present, value does NOT match
    ThreadContext.put("userid", "wronguser");
    assertSame(Filter.Result.DENY, filter.filter(null, Level.DEBUG, null, (Object) null, (Throwable) null));

    // Case 3: key absent (null value from contextData) — bug would NPE here
    ThreadContext.remove("userid");
    assertSame(Filter.Result.DENY, filter.filter(null, Level.DEBUG, null, (Object) null, (Throwable) null));

    ThreadContext.clearMap();
}
```

### Example (incorrect — only tests matching case):

```java
@Test
public void testFilterSinglePair_MissingCase() {
    // BAD: Only tests the happy path where value matches
    KeyValuePair[] pairs = new KeyValuePair[] { new KeyValuePair("userid", "testuser") };
    ThreadContextMapFilter filter = ThreadContextMapFilter.createFilter(pairs, null, null, null);
    filter.start();

    ThreadContext.put("userid", "testuser");
    assertSame(Filter.Result.NEUTRAL, filter.filter(null, Level.DEBUG, null, (Object) null, (Throwable) null));

    // Missing: ThreadContext.remove("userid") case that triggers NPE in buggy version
    ThreadContext.clearMap();
}
```