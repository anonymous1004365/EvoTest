---
name: error-handler-ref-remove-route-cleanup
description: When removing a route, ErrorHandlerBuilderRef may not clean up its onExceptionList,
  causing stale entries. This skill teaches how to test that removing an ErrorHandlerBuilderRef
  from a route properly removes its registered onExceptionList entries.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# error-handler-ref-remove-route-cleanup

## Instructions

# ErrorHandler Builder Reference Route Removal Cleanup

## Instructions

### WHEN the TG encounters:
- A method that removes or replaces a `Route` (e.g., `removeRoute()`, `addRoute()`, or route modification) on a `CamelContext`
- AND the route was wired to an `ErrorHandlerBuilderRef` (or any `ErrorHandlerBuilder` that implements `removeOnExceptionList(String routeId)`)

### THEN the TG should:

1. **Test state cleanup after route removal**: After removing a route from the `CamelContext`, verify that the `ErrorHandlerBuilder`'s internal `onExceptionList` no longer contains entries associated with that route.

2. **Use `removeOnExceptionList` to check state**: Call `errorHandlerBuilder.removeOnExceptionList(routeId)` and verify it returns `false` after route removal (meaning no stale entries remain for that route).

3. **Test the route removal lifecycle**:
   - Create a route with an error handler builder reference
   - Add the route to the `CamelContext`
   - Remove the route via `context.removeRoute(routeId)`
   - Then verify the error handler builder's onExceptionList is clean

4. **Verify the size of onExceptionList**: Before removal, assert that certain operations cause the list to grow; after cleanup, assert it shrinks back (i.e., `false` from `removeOnExceptionList` or the builder shows no stale references).

### Common Pitfalls:
- **Testing only one direction**: Do NOT test only that an `onException` was added without testing cleanup when the route is removed.
- **Assuming cleanup is automatic**: Do NOT assume the `ErrorHandlerBuilderRef` automatically cleans up state when a route is removed. The bug shows that without explicit cleanup, `removeOnExceptionList` still returns `true` (stale entry remains).
- **Ignoring the `ErrorHandlerBuilderRef` delegation**: `ErrorHandlerBuilderRef` delegates `removeOnExceptionList` to its parent `ErrorHandlerBuilderSupport`. Make sure to test the *reference builder* specifically, not just a plain builder, as the delegation may differ.

### Examples:

**Correct test (catches the bug):**
```java
@Test
public void testErrorHandlerBuilderRef() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            errorHandler(new ErrorHandlerBuilderRef("myErrorHandler") {
                @Override
                public boolean removeOnExceptionList(String routeId) {
                    return super.removeOnExceptionList(routeId);
                }
            });
            from("direct:start").to("mock:result");
        }
    });
    context.start();
    // Remove the route
    context.removeRoute("route1");
    // Verify the onExceptionList is cleaned up
    // The errorHandler builder should no longer have the route's onException entries
    // If the bug is present, removeOnExceptionList returns true (stale entry)
    assertFalse("onExceptionList should be empty after route removal", 
        context.getRoute("route1").getErrorHandlerBuilder().removeOnExceptionList("route1"));
}
```

**Incorrect test (misses the bug):**
```java
@Test
public void testErrorHandlerBuilderRef() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            errorHandler(new ErrorHandlerBuilderRef("myErrorHandler"));
            from("direct:start").to("mock:result");
        }
    });
    context.start();
    // Only tests that the route was added, never checks cleanup after removal
    // This test passes even with the bug present
}
```