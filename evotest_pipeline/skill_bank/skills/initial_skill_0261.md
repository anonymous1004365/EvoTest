---
name: child-removal-state-mutation
description: Detects bugs where removing a child component from a parent fails to
  properly update internal state structures (e.g., component ID maps, child lists).
  Apply when testing removal of dynamically added components, especially those with
  auto-generated IDs.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- BOUNDARY_CHECK
- CHILD_REMOVAL
test_pattern: STATE_TEST
---

# child-removal-state-mutation

## Instructions

# Child Removal State Mutation Detection

## Instructions

- WHEN the code has logic to remove a child component from a parent container/component (e.g., using a `remove()` method that delegates to a parent),
  - THEN the test MUST verify that after removal, the component's internal state is consistent: the removed child is no longer present in any child collection, map, or ID tracking structure.
  - Specifically, verify that:
    1. The removed component is not returned by a `get()` method on the parent.
    2. The removed component's ID is not present in any internal ID-to-component map.
    3. Adding a new component with the same auto-generated ID after removal works correctly.
  
- WHEN a component is removed during a rendering phase or iteration,
  - THEN the test MUST check that the removal is tracked properly (e.g., using a removal list/queue) so that iteration over children does not skip or double-process siblings.

- Common pitfalls:
  - Testing only that `remove()` returns true or does not throw, without verifying that the parent's internal maps/lists are updated.
  - Failing to test the scenario where a removed component is re-added (e.g., with auto-generated ID) after removal.
  - Assuming removal from a visual/parent list is sufficient without checking underlying state structures.

- Example (correct):
```java
// Given a parent with a child that has auto-generated ID
parent.add(child);
String childId = child.getId();
parent.remove(child);
// Then: parent should no longer find the child by ID
assertNull(parent.get(childId));
// And: re-adding should work
Component newChild = new SomeComponent();
parent.add(newChild);
assertNotNull(parent.get(newChild.getId()));
```

- Example (incorrect — missing state check):
```java
parent.add(child);
parent.remove(child);
// Only checks removal doesn't throw — misses state inconsistency
// Should also check: assertNull(parent.get(child.getId()));
```