---
name: transparent-container-recursion-guard
description: When a TransparentWebMarkupContainer delegates component resolution via
  component tree navigation, the TG should test that nested transparent containers
  don't cause infinite recursion (StackOverflowError) during AJAX requests or component
  rendering.
code_tags:
- INFINITE_RECURSION
- COMPONENT_TREE_NAVIGATION
test_pattern: EXCEPTION_TEST
---

# transparent-container-recursion-guard

## Instructions

# Transparent Container Recursion Guard Test

## Instructions

WHEN the TG encounters `TransparentWebMarkupContainer` that overrides `findChildComponent(ComponentTag)` or uses `ComponentResolvers.resolveByComponentHierarchy()` to delegate component lookup to sibling/child components,

THEN the TG should write a test that:

1. Creates a page with nested `TransparentWebMarkupContainer` instances (at least 2 levels deep), where one transparent container is added **as a child of another transparent container**, possibly with sibling components inside.

2. Performs an **AJAX request** (via `wicket-ajax.js` or `Wicket.Ajax.ajax()`) targeting a component nested inside the transparent hierarchy, and verifies the request completes without a `StackOverflowError`.

3. Specifically test the scenario where a `TransparentWebMarkupContainer` has a sibling component (e.g., a `Label` or `Panel`) that is an `AbstractDefaultAjaxBehavior` target, and the transparent container contains **another** `TransparentWebMarkupContainer` nested inside it.

4. Assert that `tester.executeAjaxUrl(...)` returns a non-null response and the page re-renders correctly (no uncaught exception in the wicket runtime).

**Common pitfalls to avoid:**
- Testing only a single `TransparentWebMarkupContainer` in isolation without nesting — the recursion bug manifests only when transparent containers are nested.
- Testing only regular component rendering (non-AJAX) — the bug may only trigger during AJAX request processing.
- Assuming that `setResponsePage(...)` or `assertRenderedPage(...)` after the AJAX request will detect the bug — the `StackOverflowError` may occur before the page can render.
- Using `tester.assertComponentOnAjaxResponse(...)` as the only assertion — the error occurs during request handling, not response rendering.
- Forgetting that the AJAX target component must be **inside** the transparent container hierarchy (not outside it) for the bug to trigger.

**Good example:**
```java
@Test
public void ajaxRequestForComponentInTransparentWebMarkupContainerShouldntCauseStackOverflow()
{
    tester.startPage(new DoubleNestedTransparentContainerWithSiblingTransparentContainerPage());
    tester.executeAjaxUrl(new AjaxRequestTargetListener()
    {
        @Override
        public void updateAjaxRequestTarget(AjaxRequestTarget target)
        {
            target.add(tester.getComponentFromLastRenderedPage("outer:label"));
        }
    });
    tester.assertNoErrorMessage();
    tester.assertRenderedPage(DoubleNestedTransparentContainerWithSiblingTransparentContainerPage.class);
}
```

**Bad example (tests only a single transparent container, no nesting):**
```java
@Test
public void testSingleTransparentContainerAjax()
{
    // This test would pass even with the buggy code, missing the recursion entirely
    tester.startPage(new SimpleTransparentContainerPage());
    tester.executeAjaxUrl(...);
    // No StackOverflowError because there's only one transparent container
}
```