---
name: component-removal-iterator-safety
description: When adding or removing child components in a Wicket component tree during
  rendering, iteration over the children collection must safely handle concurrent
  modifications. This skill teaches how to test that removals during rendering do
  not cause ConcurrentModificationException.
code_tags:
- COMPONENT_TREE_NAVIGATION
- CHILD_REMOVAL
- CONDITIONAL_BRANCH
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# component-removal-iterator-safety

## Instructions

# Component Removal During Tree Iteration Safety

## Instructions

WHEN the TG encounters code that adds or removes child components (via `add()`, `remove()`, `replace()`, `removeAll()`) inside a method that is called during component rendering, especially in:
- `onInitialize()`, `onBeforeRender()`, `onRender()`, `onComponentTag()`, or similar lifecycle callbacks
- A `Panel` or other container that is used inside an `ajax` region or `WebMarkupContainer`

THEN the TG should:
1. Create a test where a component dynamically adds or removes children during rendering (e.g., inside `onInitialize()` or a behavior's callback).
2. Use an Ajax-based page or an Ajax rendering request to trigger the rendering path that causes the bug.
3. Verify that the render completes without throwing a `ConcurrentModificationException` during iteration over the children list.
4. Specifically, test by adding a child panel that, in its own lifecycle, modifies the parent container's children (e.g., removing itself or a sibling from the parent).
5. Also verify that after the modification, the component counts, rendering output, and state are correct (e.g., the expected markup is generated, no missing components).

Common pitfalls:
- Testing only component addition without removal during rendering.
- Using only direct rendering without an Ajax request (the bug may only manifest under Ajax rendering paths where the component tree is re-rendered with `setOutputMarkupId(true)`).
- Assuming a panel that removes itself will work identically to one that removes a sibling — test both patterns.
- Forgetting to call `setRenderBodyOnly(false)` or `setOutputMarkupId(true)` when required by the rendering context.
- Not checking for `ConcurrentModificationException` specifically — the test should expect no exception at all, or assert that no exception of that type is thrown.

### Correct Example (catching the bug):
```java
// In a test: add a panel that modifies parent's children in its own lifecycle
@Test
public void testWithPanelAjax() {
    tester.startPage(new HomePage());
    // If the HomePage contains a MyPanel that adds/removes children during rendering,
    // and uses setOutputMarkupId(true), the Ajax request may trigger a ConcurrentModificationException.
    // The test passes when no exception is thrown.
    tester.assertNoErrorMessage();
    tester.assertNoException();
}
```

### Incorrect Example (missing the bug):
```java
@Test
public void testWithPanelAjax() {
    tester.startPage(new HomePage());
    // BUG: Only checks that the page renders, not that component removal during
    // Ajax-rendering doesn't cause ConcurrentModificationException.
    tester.assertRenderedPage(HomePage.class);
}
```