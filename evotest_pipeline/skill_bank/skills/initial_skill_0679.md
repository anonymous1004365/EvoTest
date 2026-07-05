---
name: node-dotdot-resolution-testing
description: When testing JCR session Node.hasNode() with ".." (dot-dot) path segments,
  the bug was that hasNode("..") incorrectly returned false when the current node
  is the root node. This skill teaches how to test parent-resolution via dot-dot paths
  in JCR, especially at the root node boundary.
code_tags:
- NULL_CHECK
- EXCEPTION_HANDLING
- VALIDATION
test_pattern: STATE_TEST
---

# node-dotdot-resolution-testing

## Instructions

# Dot-Dot ("..") Path Resolution in JCR hasNode()

## Instructions

- WHEN the TG encounters code that calls `Session.getNode()` or `Node.hasNode()` or similar JCR path resolution methods (like `Item.getPath()`, `Session.itemExists()`, `Node.getNode()`) where the path argument might contain `".."` (parent directory) segments
- THEN the TG should write tests that verify `".."` resolves correctly to the parent node. Specifically:
  - Call `session.getRootNode().hasNode("..")` and assert it returns `true` because the parent of the root node is still the root node itself in JCR
  - Call `session.getNode("/..")` and assert it returns the root node (i.e., `session.getRootNode()`)
  - Verify that `session.nodeExists("/..")` returns `true`
- The test should use `javax.jcr.Session`, `javax.jcr.Node`, and `javax.jcr.RepositoryException`. The test should call `Session` methods like `getRootNode()`, `getNode(String)`, `nodeExists(String)`, `hasNode(String)` on the root node.
- Common pitfalls to avoid:
  - **Do not** assume that `hasNode("..")` at the root returns `false` because the root has no parent — in JCR, the root node is its own parent, so `..` at root must resolve to root (return `true`).
  - **Do not** forget to call `session.save()` if you modify the tree before checking path resolution.
  - **Do not** test only with relative paths like `".."` on non-root nodes without also testing on the root node itself — the root boundary is where this bug manifests.
  - **Do not** assume `nodeExists()` and `hasNode()` behave identically for all path forms — test both.
  - **Do not** use `Item.getParent()` as a substitute — `getParent()` may throw `RepositoryException` on root, while `hasNode("..")` should return `true`.

### Correct Example (detects the bug)

```java
// Setup: root node exists (default state)
Session session = getAdminSession();

// Bug detection: Root node must be its own parent
assertTrue("Root hasNode('..') should return true", 
    session.getRootNode().hasNode(".."));

// Also verify via getNode
assertEquals("Root's parent via '..' should be root itself",
    session.getRootNode(),
    session.getNode("/.."));

// Verify via nodeExists
assertTrue("nodeExists('/..') should return true",
    session.nodeExists("/.."));
```

### Incorrect Example (misses the bug)

```java
// BUG: This only tests on a non-root child node
Session session = getAdminSession();
Node foo = session.getNode("/foo");

// This might pass even with the bug because
// the bug only affects the root node
assertTrue(foo.hasNode("..")); // Works on non-root nodes

// Missing: root-level ".." resolution
// The test never checks session.getRootNode().hasNode("..")
```

### What the buggy code does wrong

The buggy implementation of path resolution (in the Oak `Path` or `NodeState` resolution layer) fails to handle the `".."` segment when the current path is the root path (`"/"`). It resolves `".."` relative to root incorrectly — treating it as a non-existent parent rather than self-referencing back to root. The fixed code correctly recognizes that the parent of the root node is the root node itself, so `getAncestor(0)` for root returns root, and `hasNode("..")` returns `true`.