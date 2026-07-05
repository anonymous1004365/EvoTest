---
name: session-item-access-by-relative-path
description: When a JCR session method resolves an item by relative path where both
  a Node and a Property match, the session must return the Node (per JCR spec). This
  skill teaches how to test for correct item resolution priority.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# session-item-access-by-relative-path

## Instructions

# Session Item Resolution Priority by Relative Path

## Instructions

- WHEN the TG encounters code that calls `Session.getItem(String)` or `Session.getNode(String)` or `Session.getProperty(String)` with a relative path (e.g., `"foo/bar"`, `"child/prop"`) in a JCR repository where a child node and a property share the same relative path segment
- THEN the TG should write a test that:
  1. Obtains a JCR Session (admin or test user session)
  2. Creates a Node at a test path (e.g., under the root node)
  3. On that node, adds both a child Node and a Property with the **same name** (e.g., `"child"`)
  4. Calls `session.getItem("/testPath/child")` on the session (not on the node)
  5. Asserts that the returned `Item` is a **Node** (instanceof `javax.jcr.Node`), not a `Property`
  6. Optionally asserts that the item path equals the child node's path (e.g., `"/testPath/child"`)
- Verify the test fails on the buggy version (where the session incorrectly returned a Property) and passes on the fixed version
- **Common pitfalls to avoid:**
  - ❌ Calling `item.getParent().getChild("child")` instead of `session.getItem(...)` — the bug is specifically in the session-level item resolution, not in node-level child access
  - ❌ Only testing with a single child Node without a conflicting Property — the bug only manifests when both a Node and a Property with the same name exist at the same parent
  - ❌ Forgetting to save changes (`session.save()`) after creating nodes/properties before resolving via `getItem()`
  - ❌ Using absolute path instead of relative path when calling `getItem()` — the session's current working directory matters

### Correct Example
```java
// Setup: create a node with both a child node and a property sharing the same name
Node testNode = session.getRootNode().addNode("testNode");
testNode.addNode("collision");          // child node named "collision"
testNode.setProperty("collision", "value");  // property also named "collision"
session.save();

// Test: session.getItem should return the Node, not the Property
Item item = session.getItem("/testNode/collision");
assertTrue("Session.getItem should return Node when both Node and Property exist",
    item instanceof Node);
assertEquals("/testNode/collision", item.getPath());
```

### Incorrect Example
```java
// ❌ Wrong: testing item retrieval from the parent node, not from the session
Node testNode = session.getRootNode().getNode("testNode");
Item item = testNode.getNode("collision");  // This always returns a Node — won't catch the bug
assertNotNull(item);
```