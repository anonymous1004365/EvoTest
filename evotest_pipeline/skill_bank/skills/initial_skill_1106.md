---
name: removed-then-readded-child-reconnection
description: When a child node is removed and later re-added using the same builder
  pattern, the test must verify the re-added node correctly reflects its new state
  (e.g., child nodes are visible). This catches bugs where the builder's internal
  Head/connection state becomes stale after remove+re-add.
code_tags:
- STATE_MUTATION
- REMOVED_NODE_READD
test_pattern: STATE_TEST
---

# removed-then-readded-child-reconnection

## Instructions

# Removed-Then-Readded Child Builder Reconnection

## Instructions

- WHEN the TG encounters a tree-builder or node-builder pattern (e.g., `MemoryNodeBuilder`, `NodeBuilder`) where:
  1. A child node is obtained via `root.getChildNode("someName")` or `root.child("someName")`
  2. That child is then removed via `.remove()`
  3. The same child name is subsequently re-created via `root.child("sameName")` or `root.setChildNode("sameName", ...)`
- THEN the test MUST verify that the re-created builder's internal state is properly reconnected by checking operations that depend on fresh state, such as:
  - `x.hasChildNode("q")` should return `true` after adding a grandchild to the re-added node
  - The test should NOT assume that a builder obtained before removal remains valid for future mutations after the node is re-added
- WHEN writing such a test, the key pattern to verify is:
  ```java
  NodeBuilder root = base.builder();
  root.getChildNode("x").remove();            // remove existing child
  NodeBuilder x = root.child("x");            // re-add with same name
  x.child("q");                                // add grandchild
  assertTrue("Re-added node should have child 'q'", x.hasChildNode("q"));
  ```
- Common pitfalls to avoid:
  - Testing only the existence of the re-added node itself (e.g., `assertTrue(x.exists())`) — the bug specifically manifests when you try to access children of the re-added node
  - Getting the child builder via `root.getChildNode("x")` after re-adding (which returns a new builder) instead of using the one returned by `root.child("x")` — the stale builder from before the remove may still be cached
  - Assuming that `x.child("q")` silently succeeds means the state is correct — the bug is that `x.hasChildNode("q")` returns `false` even after `x.child("q")` was called
- The expected behavior on the buggy version is that `x.hasChildNode("q")` returns `false`, causing the assertion to fail. On the fixed version it returns `true`.