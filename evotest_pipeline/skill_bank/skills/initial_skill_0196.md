---
name: transparent-container-child-removal-during-ajax
description: When testing TransparentWebMarkupContainer with Ajax updates, child components
  that were dynamically added may be missing during re-render. This skill teaches
  how to verify that child components inside transparent containers are correctly
  removed and re-added during Ajax responses.
code_tags:
- COMPONENT_TREE_NAVIGATION
- STATE_MUTATION
- CHILD_REMOVAL
test_pattern: STATE_TEST
---

# transparent-container-child-removal-during-ajax

## Instructions

# Transparent Container Child Removal During Ajax Update

## Instructions

WHEN you encounter a `TransparentWebMarkupContainer` that contains dynamically added child components (especially other `TransparentWebMarkupContainer` instances or `Enclosure` components) that are added in `onInitialize()` or `onBeforeRender()`, AND the test performs an Ajax update on the page:

- THEN write a test that:
  1. Creates a page with a `TransparentWebMarkupContainer` as a sibling or child of another `TransparentWebMarkupContainer`
  2. Adds child components dynamically (e.g., labels, panels) to the transparent containers
  3. Triggers an Ajax behavior (e.g., `AbstractAjaxTimerBehavior`, `AjaxLink`, or `AjaxSubmitLink`) that updates the page
  4. After the Ajax response, verifies that ALL expected child components are still present and rendered, not just the parent containers
  5. Check that no `NullPointerException`, `ClassCastException`, or `ComponentNotFoundException` is thrown during re-render

- WHAT to verify:
  - After an Ajax round-trip, sibling transparent containers and their children should still be part of the component tree
  - Child components (like `Label`, `Panel`) that were inside a transparent container should still be accessible (e.g., `page.get("container:childId")` should not throw)
  - The page should render without exceptions in the Ajax response

- Common pitfalls:
  - ❌ Testing only static markup without dynamically added components — this misses the bug
  - ❌ Testing only the initial render without an Ajax round-trip — the bug manifests during re-render
  - ❌ Testing only one transparent container in isolation — the bug appears with sibling/nested transparent containers
  - ❌ Assuming that if a parent container renders, all children render correctly
  - ❌ Using only simple string/text content — the bug is more likely triggered with actual Wicket components (Labels, Panels) as children

- Example correct approach:
```java
// Page with two sibling TransparentWebMarkupContainers inside an outer one
// Add a Label to each inner container in onInitialize()
// Use a timer or AjaxLink to trigger an Ajax update
// After the Ajax call, assert that both Labels are still present and renderable
```

- Example incorrect approach:
```java
// Only renders the page once without Ajax — misses the re-render bug
// Does not add children dynamically — misses the component tree mutation