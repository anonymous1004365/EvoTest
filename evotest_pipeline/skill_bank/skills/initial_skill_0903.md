---
name: done-by-index-notification-filtering
description: When a NotifyBuilder uses whenDoneByIndex() to filter exchange completions
  by index, the TG should test that the done count tracking correctly triggers completion
  at the right time, not just when any exchange finishes.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# done-by-index-notification-filtering

## Instructions

# Done-by-Index Notification Filtering

## Instructions

- WHEN the TG encounters a NotifyBuilder using `whenDoneByIndex(int index)` to wait for a specific exchange to complete
- THEN it should write a test that:
  1. Creates a route that processes multiple exchanges (e.g., 3 or more)
  2. Calls `whenDoneByIndex(index)` where `index` is **not 0** (e.g., index 1 or 2) — this ensures the filter logic is exercised and not just matching the first exchange
  3. Uses a `whenExactlyDone(int n)` or similar done predicate to set how many exchanges must complete before the builder can fire
  4. Verifies that `matches()` returns `true` after the indexed exchange completes AND the done count is reached
- Include **concrete values**: use `whenDoneByIndex(1)` with `whenExactlyDone(3)` on a route that sends 3 messages to a direct endpoint consuming 1 per polling, and assert `builder.matches()` returns `true`
- Also test the **negative case**: set `whenDoneByIndex(someLargeIndex)` on a route that never reaches that many exchanges, and verify `matches()` returns `false` (or times out)
- **Common pitfalls to avoid**:
  - Testing only index 0 (the first exchange) — this masks bugs where done counting ignores the index filter
  - Forgetting to set a done predicate like `whenExactlyDone(n)` — without it the builder may never complete
  - Using synchronous routes that complete all exchanges before the builder starts — the route should be async or use a seda/direct endpoint with consumer threading so exchanges complete at different times
  - Not waiting long enough in the `matches(timeout)` call — exchanges may need sufficient time to process

### Correct Example (catches this bug)
```java
public void testDoneByIndex() throws Exception {
    NotifyBuilder builder = new NotifyBuilder(context)
        .whenDoneByIndex(1)
        .whenExactlyDone(3)
        .create();

    for (int i = 0; i < 3; i++) {
        template.sendBody("seda:foo", "message" + i);
    }

    assertTrue("The notification should fire when exchange[1] completes and 3 are done",
        builder.matches(5, TimeUnit.SECONDS));
}
```

### Incorrect Example (misses the bug)
```java
public void testDoneByIndex() throws Exception {
    NotifyBuilder builder = new NotifyBuilder(context)
        .whenDoneByIndex(0)   // Only tests first exchange — doesn't exercise index filter logic
        .whenExactlyDone(1)   // Only waits for 1 exchange — too trivial
        .create();

    template.sendBody("direct:foo", "test");

    assertTrue(builder.matches(5, TimeUnit.SECONDS));
}
```