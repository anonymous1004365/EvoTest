---
name: transparent-container-queue-order
description: When a TransparentWebMarkupContainer is used in a parent page and a child
  page queues components referencing the same markup ID, the dequeueing can fail due
  to order-of-resolution issues. This skill teaches how to write tests that catch
  render failures in such multi-page setups with transparent containers.
code_tags:
- COMPONENT_ADDITION_ID
- CHILD_ADDITION_REPLACE
- COMPONENT_TREE_NAVIGATION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# transparent-container-queue-order

## Instructions

# Transparent Container Dequeueing Order Skill

## Instructions

WHEN a TransparentWebMarkupContainer (or subclass like HtmlTag) is placed on a parent/base page with `wicket:id`, AND a child page (using `wicket:child`) also contains markup that references the same tag structure (e.g., `<html wicket:id="html">`),

THEN write a test that:
1. Creates both a BasePage class with a TransparentWebMarkupContainer (e.g., `HtmlTag`) added to a component ID (e.g., `"html"`), and a SubPage class that extends the BasePage and overrides the `<wicket:child/>` content
2. Renders the SubPage using `tester.startPage(SubPage.class)`
3. Asserts that rendering succeeds without throwing a `WicketRuntimeException` (or any other exception)
4. Also asserts the rendered content contains expected text from the child page (e.g., `"Sub page"`) to confirm proper dequeueing

Common pitfalls to avoid:
- Testing only the BasePage in isolation without the child page extending it — this will not trigger the order-of-resolution bug
- Using only a simple TransparentWebMarkupContainer without the `findChildComponent` override that interacts with sibling components
- Assuming that if the tag is void/self-closing (like `<img>`), the transparent container will always resolve correctly — the bug involves the order in which child components are discovered during rendering

Example of a correct test:
```java
@Test
public void startSubPageWithTWMCinTheParentPage() {
    tester.startPage(SubPage.class);
    tester.assertRenderedPage(SubPage.class);
    tester.assertContains("Sub page");
}
```

Example of an insufficient test (won't catch the bug):
```java
@Test
public void startBasePageOnly() {
    tester.startPage(BasePage.class);
    tester.assertRenderedPage(BasePage.class);
    // This passes on both buggy and fixed versions
}
```