---
name: listener-exception-handling-order
description: When testing listener-collection patterns that iterate over registered
  listeners for exception handling, verify that the first non-null handler returned
  by a listener takes precedence over subsequent listeners, preventing later handlers
  from silently overriding the first available response.
code_tags:
- LISTENER_EXCEPTION_HANDLING_ORDER
test_pattern: STATE_TEST
---

# listener-exception-handling-order

## Instructions

# Listener Exception Handling Order

## Instructions

WHEN the TG encounters a listener-collection pattern (e.g., `RequestCycleListenerCollection`, a list/array of listeners) that iterates over listeners to handle exceptions — specifically where each listener can return an `IRequestHandler` for the exception and the first non-null handler should be used — THEN the TG must:

1. **Register two listeners** that each return different handlers for the same exception, with the first listener returning a handler and the second listener also returning a (different) handler.
2. **Trigger the exception** during request processing (e.g., throw a `RuntimeException` inside a handler's `respond()` method).
3. **Assert that the first listener's handler is used**, not the second one's.
4. Use `assertEquals(expected, actual)` to compare the specific result code/state produced by the first listener's handler.

**Common pitfalls:**
- Registering only one listener – this would not catch the ordering bug because the issue is that the *second* listener incorrectly overwrites the *first* listener's handler.
- Throwing the exception outside of request processing (e.g., in a unit test that doesn't go through `processRequestAndDetach()`).
- Not checking the specific result code/state from the first listener (e.g., checking only that the exception was handled at all, not *which* handler handled it).

**Example (correct):**
```java
// Register two listeners that each return a different error code
Application.get().getRequestCycleListeners().add(new ErrorCodeListener(401));
Application.get().getRequestCycleListeners().add(new ErrorCodeListener(402));

RequestCycle cycle = newRequestCycle(new RuntimeException("testing purposes only"));
cycle.processRequestAndDetach();

// The first handler (401) should be used, NOT the second (402)
assertEquals(401, errorCode);
```

**Example (incorrect — misses the ordering bug):**
```java
// Only one listener — cannot detect if second listener overwrites the first
Application.get().getRequestCycleListeners().add(new ErrorCodeListener(401));

RequestCycle cycle = newRequestCycle(new RuntimeException("testing purposes only"));
cycle.processRequestAndDetach();

assertEquals(401, errorCode); // passes even if bug exists
```