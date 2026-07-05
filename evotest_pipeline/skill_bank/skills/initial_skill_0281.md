---
name: logged-requests-concurrent-null-handling
description: Use when iterating over a live collection (e.g., List<RequestData>) that
  can be concurrently modified by adding/removing entries, where the iteration may
  encounter null elements and cause NullPointerException. The test should verify that
  the iteration safely handles null entries without crashing.
code_tags:
- PAGE_MANAGER_STATE
- NULL_CHECK
- LOGGED_REQUESTS_ITERATION_WITH_NULL
test_pattern: STATE_TEST
---

# logged-requests-concurrent-null-handling

## Instructions

# Handling Null Entries During Live Logged Requests Iteration

## Instructions

- WHEN the code defines a method (e.g., `getLoggedRequests()`) that returns a live reference to an internal `List<RequestData>` (or similar collection) that is modified by concurrent operations (adding/removing),
- AND the code iterates over that list (e.g., in a `toString()`, `dump()`, or snapshot method) without making a defensive copy,
- THEN the TG should write a test that:
  1. Adds entries to the logged requests collection.
  2. Removes (sets to null) one entry from the live list directly to simulate a racing removal.
  3. Calls the method that iterates over the live list (e.g., `toString()` or `dump()`).
  4. Asserts that no `NullPointerException` is thrown and that the iteration completes gracefully (e.g., by checking the output does not crash).
- Include tests for both:
  - A null entry in the middle of the list.
  - A trailing null entry.
- Common pitfalls:
  - Only testing with fully populated list without null entries.
  - Assuming the list is always fully populated and stable during iteration.
  - Not directly manipulating the internal list to introduce nulls when the API does not expose a removal method.

### Example (Correct)

```java
// Given a list that is live-referenced by getLoggedRequests()
List<RequestData> liveList = logger.getLoggedRequests();
liveList.add(new RequestData(...));
liveList.add(new RequestData(...));
liveList.add(new RequestData(...));

// When the list is partially cleared (simulating concurrent removal)
liveList.set(1, null);

// Then iterating should not throw NullPointerException
String result = logger.dump();
assertNotNull(result); // completes gracefully
```

### Example (Incorrect / Pitfall)

```java
// ONLY tests with a fully populated list, missing null entries
List<RequestData> liveList = logger.getLoggedRequests();
liveList.add(new RequestData(...));
liveList.add(new RequestData(...));

// Does not simulate concurrent removal, so null never appears
String result = logger.dump(); // passes but doesn't catch the bug
assertNotNull(result);
```