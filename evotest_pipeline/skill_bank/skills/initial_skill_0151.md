---
name: detach-removed-children-visitation
description: When testing component trees with removeAll() followed by detach(), verify
  that removed children are not visited during detach. This skill addresses the bug
  where a removed child component could be visited during its parent's detach traversal,
  potentially accessing stale detachable models.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# detach-removed-children-visitation

## Instructions

# Testing Detach After removeAll() in Component Trees

## Instructions

- WHEN the TG encounters a component tree where `removeAll()` is called on a parent container (e.g., `MarkupContainer`) before `detach()` is called on that parent
- THEN the TG should write a state test that verifies the detach process does **not** visit children that were removed via `removeAll()`. The test should:
  1. Create a parent container (e.g., a `MarkupContainer` or `Page`)
  2. Add a child component (e.g., a `Label`) that has a detachable model (e.g., `new DetachableModel<>(...)`)
  3. Call `removeAll()` on the parent to remove all children
  4. Track whether the child's model's `detach()` is called (use a boolean flag or spy)
  5. Call `detach()` on the parent
  6. Assert that the removed child's model `detach()` was **NOT** called

- Common pitfalls to avoid:
  - **Testing only with non-detachable children**: The bug only manifests when the child has a detachable model whose `detach()` is called. If the child doesn't implement `IDetachable`, the bug won't be visible.
  - **Calling `remove()` on individual children instead of `removeAll()`**: The bug is specific to the `removeAll()` path, which clears the component collection differently than individual `remove()` calls.
  - **Forgetting to call `detach()` on the parent**: The bug occurs during the parent's detach traversal, so `detach()` must be called on the parent container.

### Correct Example
```java
// Create a page/container
Page page = new Page();
// Add a child with a detachable model
final boolean[] detached = {false};
page.add(new Label("child", new AbstractReadOnlyModel<String>() {
    @Override
    public void detach() {
        detached[0] = true;
    }
}));
// Remove all children
page.removeAll();
// Detach the parent
page.detach();
// Verify the child's detach was NOT called
assertFalse("Removed child should not be detached", detached[0]);
```

### Incorrect Example (Pitfall)
```java
// WRONG: Testing without verifying detach behavior
Page page = new Page();
page.add(new Label("child", "simple string"));
page.removeAll();
page.detach();
// No assertion about detach behavior - passes even on buggy version
```