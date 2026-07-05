---
name: enclosure-child-removal-visibility-reset
description: WHEN a Wicket Enclosure component has children that may be removed during
  rendering (e.g., by an AjaxFallbackLink that detaches them via remove), THEN test
  that the Enclosure's child visibility tracking correctly handles the removal without
  throwing an IndexOutOfBoundsException.
code_tags:
- CHILD_REMOVAL
- ENCLOSURE_INTERACTION
test_pattern: STATE_TEST
---

# enclosure-child-removal-visibility-reset

## Instructions

# Enclosure Child Removal During Rendering

## Instructions

- WHEN the TG encounters a test scenario where a Wicket `Enclosure` component contains child components that are **removed from the parent during rendering** (e.g., in `onClick` of an `AjaxFallbackLink` or similar link behavior)
- THEN the TG should write a test that:
  1. Creates a page with an `Enclosure` that wraps a non-WebMarkupContainer child (e.g., `Label`)
  2. Adds another child component (e.g., another `Label`) to the Enclosure's parent container before the Enclosure itself
  3. Includes a link (e.g., `AjaxFallbackLink`) that removes the first child component from the Enclosure
  4. Renders the page twice (e.g., `tester.startPage(page)` called twice or after link click)
  5. Verifies that the second render succeeds without throwing an `IndexOutOfBoundsException`

- Common pitfalls the TG might fall into:
  - Testing only with `WebMarkupContainer` children inside the Enclosure — the bug manifests when the Enclosure directly wraps a non-WebMarkupContainer component like a `Label`
  - Not adding an extra child component (like a second `Label`) to the same parent **before** the Enclosure — this is needed to trigger the index miscalculation
  - Testing only a single render pass — the bug requires two renders (first to set up children list, second after the child is removed)
  - Not testing with an `AjaxFallbackLink` or similar mechanism that removes a child of the Enclosure during rendering

- Correct approach: The test must ensure that after a component inside the Enclosure is removed, the Enclosure's internal `children` list is correctly rebuilt, preventing an `IndexOutOfBoundsException` when the Enclosure iterates its children during markup rendering.

- Example of correct test code:
```java
// Arrange: page with Enclosure wrapping a Label, plus a link that removes that Label
// The Enclosure's parent has another Label added BEFORE the Enclosure
Page page = new Page() {
    @Override
    protected void onInitialize() {
        super.onInitialize();
        add(new Label("label0")); // child added before Enclosure
        add(new Enclosure("enclosure") {
            @Override
            protected void onInitialize() {
                super.onInitialize();
                add(new Label("label1")); // non-WebMarkupContainer child
                add(new AjaxFallbackLink<Void>("link") {
                    @Override
                    public void onClick(AjaxRequestTarget target) {
                        getParent().remove(get("label1")); // remove the Label from Enclosure
                    }
                });
            }
        });
    }
};

// Act: render twice
tester.startPage(page);
tester.startPage(page);
// Assert: no IndexOutOfBoundsException occurs on second render
```

- Example of **incorrect** (too simple) test code that would miss the bug:
```java
// WRONG: Only WebMarkupContainer children, or no child before Enclosure, or single render
Page page = new Page() {
    add(new Enclosure("enclosure")
        .add(new WebMarkupContainer("child")));
};
tester.startPage(page);
// Bug does NOT trigger here
```