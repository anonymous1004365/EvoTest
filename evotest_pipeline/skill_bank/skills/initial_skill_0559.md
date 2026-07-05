---
name: parent-reference-consistency-after-add
description: When adding a child element to a parent container that maintains a parent
  reference in the child, verify that the parent reference is correctly set both in
  the child AND that the child appears in the parent's child list. This skill helps
  catch bugs where a parent set operation is missing on one side of the bidirectional
  relationship.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- PARENT_SET_UPDATES_AFTER_ADD
test_pattern: STATE_TEST
---

# parent-reference-consistency-after-add

## Instructions

# Parent Reference Consistency After Child Addition

## Instructions

- WHEN the TG encounters code that adds a child element to a parent container (e.g., `parent.addChild(child)`) AND the child has a `setParent(...)` or `setParent(...)` call that updates the child's parent reference,
- THEN the TG should verify that BOTH sides of the bidirectional relationship are consistent after the add operation:
  1. The child's `getParent()` returns the parent it was added to.
  2. The parent's child collection (e.g., `getChildren()`, `getAllElements()`) actually contains the added child.
- WHEN the parent (e.g., `CtElement`) has a method like `updateAllParentsBelow()` that propagates parent changes to descendants,
- THEN the TG should test scenarios where a child is added to a parent AND then check that `updateAllParentsBelow()` (or equivalent propagation) is called to maintain consistency. If the propagation is missing, the added child or its descendants may have a stale/null parent reference.
- WHEN testing parent-child consistency, include tests with:
  - Adding a single child and verifying `getParent()` on the child is non-null and equals the parent.
  - Adding a child that already has children (nested structure) and verifying `getParent()` on all descendants.
  - Adding multiple children and verifying each has the correct `getParent()`.
- Common pitfalls to avoid:
  - ❌ Testing only that `addChild()` returns successfully without checking `getParent()` on the added child.
  - ❌ Testing only one side (e.g., checking the child appears in parent's list) without checking the child's parent reference.
  - ❌ Assuming that `setParent()` is automatically called inside `add()` without verifying it in the actual add implementation.
  - ❌ Not testing nested/scenario where a child with sub-elements is added and only the direct child's parent is verified.
- Correct test example:
  ```java
  // Create a parent element
  CtElement parent = factory.createClass("Parent");
  // Create a child element
  CtElement child = factory.createClass("Child");
  // Add child to parent
  parent.addChild(child);
  // Verify BOTH sides of the relationship
  assertNotNull("Child's parent must not be null", child.getParent());
  assertEquals("Child's parent must be the added parent", parent, child.getParent());
  assertTrue("Parent must contain the added child", parent.getChildren().contains(child));
  ```
- Incorrect test example:
  ```java
  // ❌ Only verifies the add succeeded, but misses parent reference check
  parent.addChild(child);
  assertTrue(parent.getChildren().contains(child));
  // The child.getParent() might still be null or point to old parent!
  ```