---
name: rebase-preserves-new-child-nodes
description: When a NodeBuilder performs a rebase operation, any newly added child
  nodes that were created on the builder before rebase must still be visible after
  rebase. Use this skill to validate that rebase does not lose newly added mutable
  child nodes.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- CHILD_ADDITION_REPLACE
- CLONE_MUTATION
test_pattern: STATE_TEST
---

# rebase-preserves-new-child-nodes

## Instructions

# Rebase Preserves New Child Nodes

## Instructions

- WHEN the TG encounters a NodeBuilder (or similar builder/state object) that supports a `rebase()` operation which updates the builder's base state from an external source (e.g., another concurrent builder or root state),
- THEN the TG should write a test that:
  1. Creates a parent builder
  2. Adds a brand-new child node to that builder (e.g., `builder.child("newNode")`)
  3. Does NOT save/commit the parent builder yet
  4. Modifies the external source (e.g., another builder backed by the same root state) in a way that a rebase would apply changes
  5. Calls `rebase()` on the original parent builder
  6. Verifies that the newly added child node (`"newNode"`) still exists and is accessible after rebase by calling `builder.getChildNode("newNode")` — it should return non-null
  7. Also verify that the child's builder is the same object (or an equivalent mutable builder) by checking that further mutations on it still work (e.g., `child.setProperty("key", "value")` after rebase)

- The test should be written to FAIL on the buggy version:
  - On the buggy version, after rebase, `getChildNode("newNode")` may return `null` because rebase incorrectly discards new nodes added before the rebase call
  - On the fixed version, the child node must survive the rebase

- **Common pitfalls to avoid**:
  - Testing rebase only with pre-existing nodes (nodes that existed in the base state) — this skill specifically targets **newly added** nodes
  - Using `save()` or `commit()` before rebase — the whole point is that the new child exists only on the uncommitted builder's in-memory state
  - Only checking for `null` vs non-null — also verify the child builder is mutable after rebase by calling setter methods on it
  - Using `getChildNodeEntries()` or similar iteration that may have a different code path than `getChildNode(name)` — test both if possible

- **Example (correct approach)**:
  ```java
  NodeBuilder rootBuilder = store.getRoot().builder();
  NodeBuilder parent = rootBuilder.child("parent");
  
  // Add a new child that doesn't exist in the base state
  NodeBuilder newChild = parent.child("newNode");
  newChild.setProperty("original", "value");
  
  // Simulate external change that triggers rebase
  rootBuilder.child("other").setProperty("p", "v");
  
  // Rebase the parent builder
  parent.rebase();
  
  // Verify the new child survived the rebase
  assertNotNull("Newly added child was lost after rebase", parent.getChildNode("newNode"));
  
  // Verify the child is still mutable
  parent.getChildNode("newNode").setProperty("afterRebase", "works");
  assertEquals("works", parent.getChildNode("newNode").getString("afterRebase"));
  ```

- **Example (incorrect approach — would miss the bug)**:
  ```java
  NodeBuilder rootBuilder = store.getRoot().builder();
  NodeBuilder parent = rootBuilder.child("parent");
  
  // Only testing with pre-existing child nodes
  NodeBuilder child = parent.getChildNode("existingChild");
  child.setProperty("modified", "value");
  
  rootBuilder.rebase();
  
  // This passes on both buggy and fixed versions, missing the bug
  assertNotNull("Existing child preserved", parent.getChildNode("existingChild"));
  ```