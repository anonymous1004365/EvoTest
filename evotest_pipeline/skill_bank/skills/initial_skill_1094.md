---
name: stale-node-item-state-validation
description: WHEN the TG encounters a method that performs operations on a session
  item (like Node or Property) that may have been removed or become stale, THEN it
  should test that calling methods on the stale item throws an InvalidItemStateException.
  This skill ensures the TG validates that stale items guard against all public API
  calls.
code_tags:
- STALE_ITEM_CHECK
test_pattern: EXCEPTION_TEST
---

# stale-node-item-state-validation

## Instructions

# Stale Node Item State Validation

## Instructions

- WHEN the TG encounters a `Node`, `Property`, or `Item` implementation that calls `checkStatus()` at the beginning of its API methods, AND `checkStatus()` throws `InvalidItemStateException("stale")` when `dlg.isStale()` returns `true`, THEN the TG should verify that ALL relevant public methods on the item correctly throw `InvalidItemStateException` when invoked on a stale (e.g., removed) node.

- WHEN testing a stale item scenario, THEN the TG should:
  1. Create a session, get a node (e.g., `/test_node`), get a child node or the node itself.
  2. Remove the node via the session (e.g., `root.getNode("test_node").remove()`).
  3. Save the session to make the removal persistent and mark the item as stale.
  4. Then call the method to test on the stale item (e.g., `staleNode.getParent()`, `staleNode.getPath()`, `staleNode.getProperty("...")`, `staleNode.getNode("...")`, `staleNode.addNode("x")`, `staleNode.setProperty(...)`, etc.).
  5. Assert that the call throws `InvalidItemStateException`.

- WHEN selecting which methods to test, THEN include at least: `getParent()`, `getPath()`, `getProperty(String)`, `getNode(String)`, `addNode(String)`, `setProperty(String, ...)`, `remove()`, `isNew()`, `isModified()`, `accept(ItemVisitor)`, and any other public methods that call `checkStatus()` first.

- Common pitfalls to avoid:
  - Testing only `getParent()` or `getPath()` on a stale node while missing other methods like `getNode()`, `getProperty()`, `setProperty()`, or `addNode()`.
  - Forgetting to `save()` the session after removing the node — without saving, the stale check may not be triggered.
  - Testing stale behavior on a node that was removed but the item reference was obtained AFTER removal (not a stale reference). The item must have been obtained BEFORE removal.

- Correct example:
  ```java
  // Session already has a node at "/test_node"
  Session session = getAdminSession();
  Node root = session.getRootNode();
  Node node = root.getNode("test_node");
  node.remove();
  session.save();
  // node is now stale
  try {
      node.getParent();
      fail("Expected InvalidItemStateException");
  } catch (InvalidItemStateException e) {
      // expected
  }
  ```

- Incorrect example (missing `save()`):
  ```java
  Session session = getAdminSession();
  Node node = session.getRootNode().getNode("test_node");
  node.remove();
  // Missing session.save() — node may not be stale yet!
  try {
      node.getPath(); // This may not throw because remove() hasn't been persisted
  } catch (InvalidItemStateException e) {
      // This test may pass or fail nondeterministically
  }
  ```