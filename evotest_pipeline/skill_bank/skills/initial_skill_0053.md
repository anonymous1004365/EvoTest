---
name: route-lifecycle-state-verification
description: When testing route lifecycle operations like suspend/resume/stop, the
  TG must verify the actual route state after each operation using getRouteStatus()
  and assert that the transition completed. This catches bugs where the state reported
  by getRouteStatus() does not match the expected state after a lifecycle operation.
code_tags:
- ROUTE_LIFECYCLE
- STATE_TRANSITION
- CONCURRENCY
test_pattern: STATE_TEST
---

# route-lifecycle-state-verification

## Instructions

# Route Lifecycle State Verification

## Instructions

- WHEN the TG tests route lifecycle operations such as `suspendRoute()`, `resumeRoute()`, or `stopRoute()` on a `CamelContext`:
  - THEN it must verify the route state **after** each lifecycle operation by calling `context.getRouteStatus(routeId)` and asserting the expected state.
  - Specifically, after `suspendRoute()` is called, the TG must assert that `context.getRouteStatus(routeId)` returns `ServiceStatus.Suspended` (not `ServiceStatus.Started` or any other state).
  - After `resumeRoute()` is called, assert that the status returns to `ServiceStatus.Started`.
  - After `stopRoute()`, assert that the status returns to `ServiceStatus.Stopped`.
  - The TG should NOT assume that a lifecycle method call has succeeded just because it didn't throw an exception — the route status must be explicitly checked.
  - Include a timeout/timing element: some lifecycle operations are asynchronous. Use `Thread.sleep()` or polling with a timeout (e.g., loop checking `getRouteStatus()` for up to 5 seconds) to verify the state transition eventually completes.
  - Common pitfall: Only verifying that no exception was thrown when calling `suspendRoute()` / `resumeRoute()`, without actually checking the route's status. This misses bugs where the route reverts to a previous state (e.g., `Started` instead of `Suspended`).

**Example (correct):**
```java
// CORRECT: Verify the state after each lifecycle operation
context.startRoute("foo");
assertEquals(ServiceStatus.Started, context.getRouteStatus("foo"));

context.suspendRoute("foo");
Thread.sleep(100); // allow async processing
assertEquals(ServiceStatus.Suspended, context.getRouteStatus("foo"));

context.resumeRoute("foo");
Thread.sleep(100);
assertEquals(ServiceStatus.Started, context.getRouteStatus("foo"));
```

**Example (incorrect — missing state check):**
```java
// INCORRECT: Only checks that no exception was thrown
context.suspendRoute("foo"); // no exception, but route may still be Started!
// Missing: assertEquals(ServiceStatus.Suspended, context.getRouteStatus("foo"));
```