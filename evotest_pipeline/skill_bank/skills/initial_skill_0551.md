---
{}
---

---
name: session-invalidate-then-access
description: WHEN the code allows invalidating a session (e.g., Session.invalidate()) and later accessing session-bound state (attributes, sessions store) THEN test that invalidating the session and immediately checking session attributes throws an appropriate exception (e.g., IllegalStateException). Common pitfall: testing only the invalidation call without verifying that subsequent session access fails cleanly.
code_tags: ['NULL_CHECK', 'ARGUMENT_VALIDATION', 'STATE_MUTATION', 'RESOURCE_MANAGEMENT']
test_pattern: STATE_TEST
---

# session-invalidate-then-access

## Instructions

# Session Invalidate Then Access

## Instructions

- WHEN the TG encounters a method that invalidates a session (e.g., `Session.invalidate()`, `session.invalidateNow()`, or a method that sets a session-invalidated flag) and there is a separate session store or attribute getter that might be called after invalidation
- THEN the TG should write a test that:
  1. Calls the session invalidation method (e.g., `tester.getSession().invalidate()` or `session.invalidateNow()`)
  2. Then immediately attempts to access session-bound state – for example, calling a session attribute getter like `tester.getSession().getAttribute("someKey")` or interacting with the session store (e.g., `sessionStore.getAttribute(session, "key")`)
  3. Asserts that accessing session state after invalidation throws an `IllegalStateException` (or another documented exception) – the exact exception class should be verified from the code
- **Common pitfalls:**
  - Testing only that `invalidate()` returns without error, without verifying that subsequent session access fails
  - Assuming invalidation is purely a flag-setter and testing only the flag state (e.g., checking `isSessionInvalidated()` if such a method exists) instead of testing the actual runtime behavior (accessing attributes)
  - Not calling the session store's attribute accessors (e.g., `getAttribute`, `setAttribute`) after invalidation, which is where the bug manifests
  - Relying solely on the next HTTP request cycle to detect invalidation – write a test that detects it immediately within the same test method

### Correct example (conceptual – adapt to actual API):
```java
// Invalidate the session
tester.getSession().invalidate();

// Now attempt to access session attributes – this should throw
assertThrows(IllegalStateException.class, () -> {
    tester.getSession().getAttribute("someKey");
});
```

### Incorrect example (common pitfall):
```java
// Only tests that invalidate() doesn't throw – misses the bug
tester.getSession().invalidate();
// No follow-up access, so the bug (that session store is still accessed) goes undetected
```