---
name: item-queue-removal-lifecycle-validation
description: When a RefreshingView removes and readds items during rendering, items
  that are newly created and assigned a child component may still carry a stale parent
  reference that causes onRemove to skip dequeue. The TG should test that onRemove
  is correctly called for items that are created, added to a child component, then
  removed during refresh.
code_tags:
- VALIDATION
- STATE_MUTATION
- ARGUMENT_VALIDATION
- ITEM_QUEUE_REMOVAL_LIFECYCLE
test_pattern: STATE_TEST
---

# item-queue-removal-lifecycle-validation

## Instructions

# Item Queue Removal Lifecycle Validation

## Instructions

- WHEN the TG encounters a `RefreshingView` (or any repeater) that overrides `getItem()` and creates new `Item` objects, then tests them with `child` associations AND queue-based removal during re-rendering
- THEN the TG should verify that when:
  1. An `Item` is created via `newItem(String id)` (or `getItem()`)
  2. A child component is added to that Item via `item.add(child)` / `item.setDefaultModelObject(child)`
  3. The item with the child is later removed during `onRender()` iteration (i.e., items are queued, dequeued, and old items without children may be dequeued but new items with children are not properly dequeued)
- The test should verify that `onRemove()` is called on components that were added to items that are removed during rendering, because the bug causes these components to remain in the component queue (parent association not cleared properly), preventing `onRemove` from being invoked
- Specifically, test that:
  - A component added as a child of a removed Item does NOT get its `onRemove()` called after the buggy rendering cycle (i.e., its parent was not properly dequeued)
  - The correct behavior is that the component's `onRemove()` IS called (or that the component is properly removed from the queue)
- Common pitfalls:
  - Testing only the new item's addition without also verifying removal/cleanup behavior
  - Assuming that `queue.remove()` on the parent Item automatically removes all children from their queue associations
  - Using a mock `Item` that doesn't replicate the real `setParent()` / `getParent()` / queue behavior
  - Not checking `component.isRemoved()` or that `component.getParent()` is null after item removal

### Correct test approach example (in spirit):
```java
// Create a component that tracks onRemove calls
AtomicBoolean onRemoveCalled = new AtomicBoolean(false);
Component child = new Label("child", "test") {
    @Override
    protected void onRemove() {
        onRemoveCalled.set(true);
    }
};

// Add child to an Item, then add the item to the view
Item item = view.newItem("id");
item.add(child);
view.add(item);

// Render the view (causing refresh: items are dequeued and requeued)
view.renderHead(response); // or view.onRender()

// Verify the child's onRemove was called
assertTrue("onRemove should have been called", onRemoveCalled.get());
```

### Incorrect test approach example:
```java
// Testing only that the new item renders without verifying cleanup
Item item = view.newItem("id");
item.add(new Label("child", "test"));
view.add(item);
// Missing: rendering cycle that triggers removal of old items
// Missing: verification that onRemove() was called for removed children
```