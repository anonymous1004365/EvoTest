---
name: onexception-before-routes-validation
description: WHEN a RouteBuilder defines `onException()` after `from()` routes, THEN
  the test should verify that defining onException after any route triggers an IllegalArgumentException.
  This ensures the builder enforces that error handlers must be configured before
  route definitions.
code_tags:
- ORDER_DEPENDENCY
test_pattern: EXCEPTION_TEST
---

# onexception-before-routes-validation

## Instructions

# OnException Must Be Defined Before Routes

## Instructions

- WHEN a `RouteBuilder` calls `onException(Class<? extends Throwable>)` AFTER one or more `from(...)` route definitions have already been added to the route collection
- THEN the `RouteBuilder.onException()` method MUST throw an `IllegalArgumentException` with the message `"onException must be defined before any routes in the RouteBuilder"` because the `RoutesDefinition.getRoutes()` collection is no longer empty
- The TG should write a test that:
  1. Creates a `RouteBuilder` (typically using `context.addRoutes(new RouteBuilder() {...})`)
  2. Defines a route using `from("direct:start").throwException(...)` BEFORE calling `onException(...)`
  3. Does NOT use the default route builder auto-start (set `isUseRouteBuilder()` to `false` on the test class, or use `context.addRoutes(...)` manually)
  4. Wraps the `context.addRoutes(...)` call in a try-catch or uses `assertThrows(IllegalArgumentException.class, ...)`
  5. Verifies the exception message equals `"onException must be defined before any routes in the RouteBuilder"`

- **Common pitfalls to avoid:**
  - Testing with `onException()` called before any `from()` — that is the correct/valid order and will NOT throw
  - Only checking the exception type (`IllegalArgumentException.class`) without also asserting the exact message text
  - Using `isUseRouteBuilder() = true` (or not overriding it) which may cause the default route builder to auto-start and interfere with the test
  - Forgetting that the check is on `getRouteCollection().getRoutes().isEmpty()` — any prior `from()` call adds a route entry and triggers the validation

### Example: Incorrect (does not trigger the bug)

```java
// This will NOT throw — onException is called before from()
context.addRoutes(new RouteBuilder() {
    @Override
    public void configure() throws Exception {
        onException(IllegalArgumentException.class)
            .handled(true)
            .to("mock:damn");

        from("direct:start")
            .throwException(new IllegalArgumentException("Damn"));
    }
});
```

### Example: Correct (triggers the bug)

```java
public class OnExceptionAfterRouteTest extends ContextTestSupport {
    @Override
    public boolean isUseRouteBuilder() {
        return false;  // prevent auto-start of default routes
    }

    public void testOnExceptionAfterRoute() throws Exception {
        try {
            context.addRoutes(new RouteBuilder() {
                @Override
                public void configure() throws Exception {
                    from("direct:start")
                        .throwException(new IllegalArgumentException("Damn"));

                    onException(IllegalArgumentException.class)
                        .handled(true)
                        .to("mock:damn");
                }
            });
            fail("Should have thrown an exception");
        } catch (IllegalArgumentException e) {
            assertEquals("onException must be defined before any routes in the RouteBuilder", e.getMessage());
        }
    }
}
```