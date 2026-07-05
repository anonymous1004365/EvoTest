---
name: path-validation-for-same-name-sibling-nodes
description: When dealing with same-name sibling (SNS) nodes under a shared parent,
  the TG should verify that path resolution correctly distinguishes nodes by index.
  This skill teaches validating that path strings like "/foo[1]/bar[2]" resolve correctly
  and that SNS node creation works properly without path duplication errors.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- EXCEPTION_HANDLING
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# path-validation-for-same-name-sibling-nodes

## Instructions

# Path Validation for Same-Name Sibling Nodes

## Instructions

- WHEN the TG encounters code that creates or resolves node paths, especially involving same-name sibling nodes (e.g., adding multiple child nodes with the same name under a single parent like `/foo[1]/bar[1]` and `/foo[1]/bar[2]`)

- THEN the TG should write a test that:
  1. Creates multiple child nodes with the same name under a shared parent (e.g., `node.addNode("bar")` called twice on the same parent)
  2. Retrieves the children and asserts their paths include the correct SNS index, e.g., the first child should be at `/foo[1]/bar[1]` and the second child at `/foo[1]/bar[2]`
  3. Calls `session.getNode("/foo[1]/bar[2]")` with the index-suffixed path and asserts that it returns the second child successfully (not throwing PathNotFoundException or returning the wrong node)
  4. Verifies that the returned node's `getPath()` matches the expected index-suffixed path

- Common pitfalls to avoid:
  - **Testing only by name without index**: Simply asserting `getNodes("bar")` returns the correct count is insufficient — the TG must verify the indexed path resolution actually works.
  - **Using `getPath()` on the SNS nodes without checking the index suffix**: The TG must check that the second same-name sibling's path ends with `[2]`, not just `[1]` or the bare name.
  - **Calling `getNode(name)` without index on SNS nodes**: This can return the first sibling rather than the intended one. The TG should use indexed paths like `getNode("/foo[1]/bar[2]")`.

- **Correct example** (what the test should look like):
  ```java
  Node foo = session.getRootNode().addNode("foo");
  foo.addNode("bar");
  foo.addNode("bar");
  session.save();

  NodeIterator children = foo.getNodes();
  assertEquals(2, children.getNodeCount());
  
  Node child1 = session.getNode("/foo[1]/bar[1]");
  Node child2 = session.getNode("/foo[1]/bar[2]");
  
  assertEquals("/foo[1]/bar[1]", child1.getPath());
  assertEquals("/foo[1]/bar[2]", child2.getPath());
  ```

- **Incorrect example** (common mistake):
  ```java
  Node foo = session.getRootNode().addNode("foo");
  foo.addNode("bar");
  foo.addNode("bar");
  session.save();
  
  // BUG: Only testing the bare path, not the indexed path
  Node bar = session.getNode("/foo[1]/bar"); // This may fail or return wrong sibling
  ```