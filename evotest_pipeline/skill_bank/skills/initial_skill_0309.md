---
name: transparent-container-mutual-visit
description: When a transparent markup container visits inner-sibling components and
  calls locateMarkStream/writeMarkup, the visit may return to the same container,
  causing infinite recursion. The TG should test scenarios with nested TransparentWebMarkupContainers
  and sibling transparent containers involved in ajax rendering.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- COMPONENT_TREE_NAVIGATION
- COMPONENT_REMOVAL_RENDERING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# transparent-container-mutual-visit

## Instructions

# Transparent Container Mutual Visit

## Instructions

- WHEN the TG encounters a `TransparentWebMarkupContainer` that overrides `findChildComponent(ComponentTag)` and calls `renderHeadForInnerSiblings(HtmlHeaderContainer)` or `visitChildren()` on its parent (or another container), THEN the TG should write a test that builds a page containing **nested** and **sibling** `TransparentWebMarkupContainer` instances and triggers a full rendering cycle (e.g., via an AJAX request to a child component). The test must verify that no `StackOverflowError` occurs.

- Specifically, when the code uses `visitChildren()` or any traversal over children that calls back into `findChildComponent()` or other transparent lookup logic on the same container, the TG must ensure that the traversal does not re-enter the same `TransparentWebMarkupContainer` in a way that causes infinite recursion. The test should involve at least two levels of nesting and a sibling transparent container that all participate in rendering.

- **Concrete test construction**: Build a page (`WebPage`) with:
  - Outer `TransparentWebMarkupContainer` (id="outer")
  - Nested inner `TransparentWebMarkupContainer` (id="inner") added to the outer container
  - A sibling `TransparentWebMarkupContainer` (id="sibling") added to the outer container (same level as the inner container)
  - A child `WebMarkupContainer` (id="child") added to the inner container
  - Use a `TestPageRenderer` or `executeAjaxRequest` to trigger full rendering of the page or an AJAX response containing the child container

- **What to verify**: The test must assert that rendering completes without throwing a `StackOverflowError`. For example:
  - `tester.executeAjaxRequest(component);` — should not throw
  - Or use `Assert.assertNotNull(tester.getLastResponse().getDocument());` after rendering

- **Common pitfalls**:
  - Testing only a single `TransparentWebMarkupContainer` without nesting. The bug manifests only when a transparent container encounters sibling or nested transparent containers during its `findChildComponent()` or `renderHeadForInnerSiblings()` traversal, because the parent traversal leads back into a transparent container that again delegates upward.
  - Failing to trigger the actual render path. Instantiation alone does not expose the bug — you must call `render()` or `executeAjaxRequest`.
  - Testing only static rendering without AJAX. The bug can manifest in both regular and AJAX rendering, but the triggering test uses `executeAjaxRequest`.

- **Example (correct test code)**:
  ```java
  @Test
  public void ajaxRequestForComponentInTransparentWebMarkupContainerShouldntCauseStackOverflow()
  {
      tester.startPage(new DoubleNestedTransparentContainerWithSiblingTransparentContainerPage());
      tester.executeAjaxRequest(tester.getComponentFromLastRenderedPage("outer:inner:child"));
      // No StackOverflowError should occur
  }
  ```

- **Example (incorrect — too shallow)**:
  ```java
  @Test
  public void transparentContainerShouldRender() {
      tester.startPage(new SimpleTransparentContainerPage());
      tester.assertRenderedPage(...); // Only outer level, no nesting, no sibling
  }
  ```
  This test would not catch the StackOverflowError because it does not trigger the recursive traversal path through nested transparent containers.