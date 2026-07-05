---
name: transparent-container-queueing-order
description: ''
code_tags:
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# transparent-container-queueing-order

## Instructions

# Testing Component Queueing Inside Transparent Containers

## Instructions

- WHEN the TG encounters a `TransparentWebMarkupContainer` (or any container that implements `IComponentResolver`) being used as a parent for queued child components
- THEN it should write a state test that starts a page with the container, enqueues components into it, and renders the page to verify no `WicketRuntimeException` is thrown
  - The test must use `WicketTester` (or similar testing utility) to start the page
  - The test must call `tester.assertRenderedPage(ExpectedPageClass.class)` after starting
  - The test markup should include both the transparent container and components that get their children dequeued (e.g., via `DequeueingBehavior`)
  - The test should verify that all components are properly rendered and no exception occurs during component resolution

- Common pitfalls to avoid:
  - Testing only components that are directly inside the transparent container without also testing components whose children get dequeued within the transparent container context
  - Testing only the happy path where no `DequeueingBehavior` is involved
  - Forgetting that `TransparentWebMarkupContainer.findChildComponent()` may return `null` for components that were already dequeued/modified by a child component during the same iteration, leading to `WicketRuntimeException: No children component with filter...`
  - Writing unit tests that mock the container instead of using full page rendering tests that exercise the actual component resolution flow

- Example correct approach:
```java
@Test
public void queuedComponentsInsideTransparentContainer()
{
    tester.startPage(TransparentContainerQueuePage.class);
    tester.assertRenderedPage(TransparentContainerQueuePage.class);
}
```
Where `TransparentContainerQueuePage` extends `WebPage` and contains a `TransparentWebMarkupContainer` that wraps components with `DequeueingBehavior`, and the markup has proper wicket IDs that match the enqueued components.

- Incorrect approach:
```java
// WRONG: Only tests a single component without transparent container involvement
@Test
public void testDequeueingComponent()
{
    // This misses the bug because the transparent container's
    // findChildComponent logic is never exercised
    tester.startPage(SimpleDequeuePage.class);
}
```