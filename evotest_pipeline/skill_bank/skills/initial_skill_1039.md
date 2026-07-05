---
name: render-counter-tracking-with-visitchildren
description: When a component overrides onAfterRender and uses visitChildren to traverse
  child components, the visit can trigger extra render cycles that inflate render
  counts. This skill teaches the TG to test that render counts remain accurate even
  when visitChildren is called within render lifecycle methods.
code_tags:
- RENDER_COUNTER_TRACKING
- VISIT_CHILDREN_RENDER_SIDE_EFFECT
test_pattern: STATE_TEST
---

# render-counter-tracking-with-visitchildren

## Instructions

# Render Counter Tracking with visitChildren Side Effects

## Instructions

- WHEN the TG encounters a `MarkupContainer` or `Component` that overrides `onAfterRender()` (or similar render lifecycle methods like `onRender()`, `onBeforeRender()`) AND calls `visitChildren()` inside that override
- THEN the TG should write a test that:
  1. Creates a `MarkupContainer` (e.g., subclass) that overrides `onAfterRender()` to call `super.onAfterRender()` followed by `visitChildren()` with a visitor
  2. Adds at least one child component to the container
  3. Renders the container (e.g., via `render()` or `internalRender()` or by attaching to a `Page` and rendering)
  4. Checks that the render count (tracked via a counter inside the child's `onAfterRender()`) is exactly 1 — not 2, 3, or 4
  5. The test should verify that calling `visitChildren()` from within a render lifecycle method does NOT cause child components to be re-rendered (which would inflate their render count)
- The expected behavior on the buggy version is that the render counter is higher than 1 (e.g., 4 instead of 1), causing the assertion `assertEquals(1, renderCount)` to fail
- Be concrete: use `org.apache.wicket.MarkupContainer` and `org.apache.wicket.Component` with `protected void onAfterRender()` override
- Common pitfalls:
  - Testing only the parent component's render count but not the children's — the bug manifests in child render counts, not the parent's
  - Forgetting to call `super.onAfterRender()` in the override — without it, the parent's render logic (including child rendering) doesn't run properly
  - Using a mock or stub that doesn't actually trigger the full render lifecycle — the component must be rendered through its full lifecycle (e.g., by attaching to a Page that is rendered)
  - Not adding any children to the container — the bug only manifests when there are child components that `visitChildren` can find and (incorrectly) re-render
  - Testing only once and accepting any render count — the bug is about the render count being unexpectedly high (multiple renders), so the assertion must verify it's exactly 1

### Correct Example (for the test):
```java
final int[] renderCount = {0};
MarkupContainer container = new MarkupContainer("container") {
    @Override
    protected void onAfterRender() {
        super.onAfterRender();
        visitChildren((Component component) -> {
            // just visiting, no-op visitor
        });
    }
};
Component child = new Component("child") {
    @Override
    protected void onRender() {
        renderCount[0]++;
    }
    @Override
    public boolean isVisible() {
        return true;
    }
    @Override
    protected void onAfterRender() {
        super.onAfterRender();
        // child's onAfterRender records render
    }
};
container.add(child);
// Render the container through its full lifecycle
// (e.g., by adding to a Page and calling page.renderPage())
assertEquals(1, renderCount[0]);
```

### Incorrect Example (common pitfalls):
```java
// WRONG: No children added, so the bug would not manifest
MarkupContainer container = new MarkupContainer("container") {
    @Override
    protected void onAfterRender() {
        super.onAfterRender();
        visitChildren(...);
    }
};
// No child added — renderCount would be 0, missing the bug
container.render();
// WRONG: Checking parent's render count instead of children's
assertEquals(1, parentRenderCount); // Parent may render correctly, children get inflated
```