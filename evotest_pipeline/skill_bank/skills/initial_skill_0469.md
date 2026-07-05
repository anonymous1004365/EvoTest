---
name: removed-component-listener-handler
description: When testing ListenerRequestHandler with a removed/non-existing component
  on an existing (stateful) page, the test must verify that a ComponentNotFoundException
  with message "Component '...' has been removed from page." is thrown, not a generic
  "Could not find component" message. The bug was that a stale/stateful page with
  a removed component produced the wrong error message.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# removed-component-listener-handler

## Instructions

# Testing Removed Component Handling in ListenerRequestHandler

## Instructions

WHEN testing `ListenerRequestHandler.respond(IRequestCycle)` with a `PageAndComponentProvider` that points to a **non-existing component on an existing (stateful) page instance** (i.e., the page is passed as an object, not a class):

- THEN the test MUST construct `PageAndComponentProvider` using the constructor `new PageAndComponentProvider(pageInstance, componentPath)` — passing a concrete `IRequestablePage` object (e.g., `new DummyPage()`), not a `Class`.
- THEN the test MUST expect the call `new ListenerRequestHandler(pageComponentProvider).respond(requestCycle)` to throw a `WicketRuntimeException` (which `ComponentNotFoundException` extends).
- THEN the test MUST assert that the exception message equals **exactly**: `"Component 'foo' has been removed from page."` (where `foo` is the component path).
- Common pitfall: Using `PageAndComponentProvider(pageClass, pageParameters, componentPath)` (a fresh-page constructor) will NOT trigger the bug — the fresh page silently ignores the missing component, so the test passes even on buggy code. Always use the constructor taking a page **instance**, not a class.
- Another common pitfall: Asserting only that a `ComponentNotFoundException` (or `WicketRuntimeException`) is thrown without verifying the exact message. The buggy code threw `"Could not find component 'foo' on page '...'"` instead of the correct `"Component 'foo' has been removed from page."`.

### Correct Example

```java
// Non-existing component on an existing (stateful) page instance MUST throw with specific message
PageAndComponentProvider oldPage = new PageAndComponentProvider(new DummyPage(), "foo");
try
{
    new ListenerRequestHandler(oldPage).respond(tester.getRequestCycle());
    fail("Expected WicketRuntimeException for removed component");
}
catch (WicketRuntimeException ex)
{
    assertEquals("Component 'foo' has been removed from page.", ex.getMessage());
}
```

### Incorrect Example

```java
// WRONG: Using page class instead of page instance — this creates a fresh page
// so the component-not-found is silently ignored and no exception is thrown
PageAndComponentProvider freshPage = new PageAndComponentProvider(DummyPage.class, null, "foo");
new ListenerRequestHandler(freshPage).respond(tester.getRequestCycle());
// No exception — test passes even though the component doesn't exist

// WRONG: Asserting only exception type without message
catch (WicketRuntimeException ex)
{
    // This passes even on buggy code where the message is wrong
    // Should also check: assertEquals("Component 'foo' has been removed from page.", ex.getMessage());
}
```