---
name: same-name-sibling-node-path-resolution
description: When testing JCR path resolution with same-name sibling (SNS) indexes
  like /foo[1]/bar[2], the path parser must correctly handle bracket notation. The
  TG should test that getNode accepts SNS paths and does not incorrectly reject them
  as invalid.
code_tags:
- VALIDATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# same-name-sibling-node-path-resolution

## Instructions

# Same-Name Sibling Node Path Resolution

## Instructions

- WHEN the TG encounters code that validates or parses JCR paths (e.g., in `SessionContext.getNode()` or any `getNode` / `getNodes` method that interprets path strings)
- THEN the TG must test that the path parser correctly handles same-name sibling (SNS) index notation like `/foo[1]/bar[2]` — the brackets `[` and `]` and the index number inside must be accepted as valid path syntax and not cause a `RepositoryException("Invalid name or path: ...")`
- Include test cases that:
  - Use paths with SNS index notation (e.g., `/[somenode][1]`, `/somenode[1]/subnode[2]`)
  - Verify that `getNode()` returns a valid `Node` object instead of throwing a `RepositoryException`
  - If the buggy version throws `RepositoryException("Invalid name or path: " + path)`, the fixed version should successfully resolve the path and return a node
- Common pitfalls:
  - Testing only simple path strings like `/foo` or `/foo/bar` without bracket-notation indexes — this will NOT catch the bug
  - Forgetting to create the nodes first (e.g., via `getRootNode().addNode("foo")`) before attempting to access them via SNS paths
  - Assuming that SNS index `[1]` means the first child — test with `[2]` as well to verify index > 1 works
  - Not verifying the correct node is returned (e.g., if multiple same-name siblings exist, `[2]` should return the second one, not the first)

### Example (correct)

```java
// Setup: create same-name siblings
Node parent = session.getRootNode().addNode("parent");
Node childA = parent.addNode("child");
Node childB = parent.addNode("child");
session.save();

// Test that SNS paths work
Node resolved = session.getNode("/parent/child[2]");
assertEquals(childB.getPath(), resolved.getPath());
```

### Example (incorrect — will NOT catch this bug)

```java
// This only tests simple paths without SNS notation
Node node = session.getNode("/parent/child");
assertNotNull(node);
// This test passes on BOTH buggy and fixed, missing the SNS bug entirely
```