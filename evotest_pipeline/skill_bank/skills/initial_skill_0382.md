---
name: transparent-container-child-queueing
description: When adding queued child components inside a TransparentWebMarkupContainer
  that has siblings, ensure components are rendered correctly and not missed during
  dequeueing. This skill teaches how to test child component addition within transparent
  resolvers that share a parent container.
code_tags:
- CHILD_ADDITION_REPLACE
- COMPONENT_TREE_NAVIGATION
- STATE_MUTATION
- COMPONENT_REMOVAL_RENDERING
test_pattern: INTERACTION_TEST
---

# transparent-container-child-queueing

## Instructions

# Transparent Container Child Queueing

## Instructions

WHEN the test code adds child components (queued or directly added) INSIDE a `TransparentWebMarkupContainer` that has sibling containers ALSO inside the same parent `WebMarkupContainer`:

- THEN the test MUST verify that ALL child components are rendered in the output markup, not just some of them.
- Specifically, create a page where a parent `WebMarkupContainer` contains both a `TransparentWebMarkupContainer` as a direct child AND other sibling containers (also `TransparentWebMarkupContainer` or regular containers).
- Add child components (e.g., `Label`, `Panel`, `Link`) inside the first `TransparentWebMarkupContainer`.
- Render the page with `tester.startPage()` and assert that the markup contains ALL expected child component outputs (e.g., label text, link tags).
- A common mistake is to test only the `TransparentWebMarkupContainer` in isolation without siblings — the bug only manifests when sibling containers exist within the same parent.
- Another pitfall is to forget that `TransparentWebMarkupContainer` resolves its children via `ComponentResolvers.resolveByComponentHierarchy()`, which traverses the component tree during rendering. When a sibling container is added BEFORE the first one's children in the markup stream, the dequeueing may skip children of the first container.
- Use `tester.assertLabel("componentId", "expectedText")` or `tester.assertContains("expectedText")` to verify each child is present in the rendered response.
- Expect `MarkupException` (or a missing component error) on the buggy version if a queued child inside a transparent container with siblings is not found.

Example of what should trigger the test:
```java
// Correct test approach
WebPage page = new WebPage() {
    @Override
    protected void onInitialize() {
        super.onInitialize();
        WebMarkupContainer parent = new WebMarkupContainer("parent");
        add(parent);

        // Sibling containers inside the same parent
        TransparentWebMarkupContainer first = new TransparentWebMarkupContainer("first");
        parent.add(first);

        TransparentWebMarkupContainer second = new TransparentWebMarkupContainer("second");
        parent.add(second);

        // Queue components inside the first transparent container
        first.queue(new Label("child1", "hello"));
        first.queue(new Label("child2", "world"));
    }
};
```

Common pitfalls to avoid:
- ❌ Testing a `TransparentWebMarkupContainer` that has no sibling containers — this does NOT trigger the bug.
- ❌ Only testing components directly in the parent page (not inside a nested transparent container).
- ❌ Forgetting that the bug is about component **resolution during rendering**, not about component addition per se.
- ✅ Always include sibling containers in the same parent, and verify that all queued children inside each transparent container are rendered.