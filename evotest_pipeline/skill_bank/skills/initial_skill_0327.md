---
name: dispatch-event-ordering
description: This skill teaches how to test that dispatchers preserve event ordering
  and correctly dispatch all pending events, even when new events are created during
  dispatch. Use it when testing event dispatch loops that create new events as part
  of processing existing ones.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# dispatch-event-ordering

## Instructions

# Dispatch Event Ordering Test

## Instructions

- WHEN the TG encounters a `dispatch()` method that processes events from a queue and creates new events during dispatch (e.g., by calling methods on the same dispatcher or modifying the same queue)
- THEN the TG should write a test that:
  1. Sets up the dispatcher and adds initial events to the queue
  2. Configures the event handlers such that processing some events creates new events (e.g., on `NodeState` change, a commit triggers a background operation that dispatches more events)
  3. Calls `dispatch()` and verifies that ALL events are eventually processed, including those created during dispatch
  4. Verifies the total event count after dispatch matches the sum of initially queued events plus any events created during processing
  5. Uses a `CountDownLatch` or `Semaphore` to detect when all expected events have been processed

- WHEN testing a dispatcher that uses a snapshot of events (as in the copy-on-iterate pattern), the TG should verify that events added during dispatch are NOT lost after the loop exits
- The TG should verify that the dispatch terminates successfully without throwing exceptions like `IllegalStateException` or `ConcurrentModificationException`
- Common pitfalls to avoid:
  - Testing only the initial set of events without verifying events created during dispatch
  - Assuming that iterating a copy of the event list is sufficient — the TG must check that newly added events are also processed in a subsequent iteration
  - Testing only single-threaded scenarios when the dispatcher may be called from multiple threads

### Correct Example (catching the bug)

```java
// Configure dispatcher and event producers such that
// processing event A creates event B.
// Add initial events to the dispatcher.
// Call dispatch() and verify all events A, B, C, ... are processed.
// Use a CountDownLatch to track processed event count.
// Expect dispatch() to return successfully and all events to be accounted for.
```

### Incorrect Example (missing the bug)

```java
// Only add initial events and call dispatch().
// Verify only the initial events were processed.
// This misses events added during dispatch.
```