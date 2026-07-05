---
name: relative-node-include-proxy-visit
description: When a node include has a relativeNode flag set to true, the aggregate
  must correctly visit child nodes via the proxy root. Test that both direct and relative
  node includes properly traverse child nodes within the aggregate node tree.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STATE_MUTATION
- PROXY_PATTERN
test_pattern: STATE_TEST
---

# relative-node-include-proxy-visit

## Instructions

# Relative Node Include Proxy Visit

## Instructions

- WHEN the TG encounters an `Aggregate` class with an inner `NodeInclude` class that has a `boolean relativeNode` field and a `NodeIncludeResult` inner class with `List<String> relativeNodeProperties`
- THEN it should write a test that:
  1. Creates an `Aggregate` with a `NodeInclude` where `relativeNode = true` and a node type pattern like `"nt:base"` or a specific relative path
  2. Creates a test node tree under a root node (e.g., `testRoot`) that contains both:
     - A child node matching the include type/pattern (e.g., `childNode`)
     - A grandchild node under that child (e.g., `childNode/grandChild`)
  3. Calls `aggregate.getIncludes()` and iterates over includes to collect the `NodeIncludeResult` objects by calling `include.collectResults(...)` on the test node tree
  4. Asserts that for each `NodeIncludeResult`, the `relativeNodeProperties` list contains the expected properties from both the child and grandchild nodes
  5. Specifically verifies that the count of indexed nodes is correct (e.g., `assertEquals(2, nodeStates.size())`) — the bug was that `relativeNode=true` includes failed to traverse/visit child nodes under the relative node root, causing missing results

- WHEN constructing test data:
  - Use a `NodeState` tree builder (e.g., `TreeIoUtils` or `NodeBuilder`) to create a multi-level hierarchy
  - Ensure the node tree has at least 2 levels of depth under the relative node include target
  - Set properties on both levels so the aggregate includes should pick them up

- Common pitfalls to avoid:
  - Do NOT test only with `relativeNode = false` — the bug specifically affects the `relativeNode = true` path
  - Do NOT create a flat node tree — the bug manifests when there are child nodes under the relative node target
  - Do NOT forget to verify the number of results collected — the bug causes fewer results than expected
  - Do NOT assume that aggregate collection works identically for direct includes and relative node includes — they use different traversal logic

- Correct example:
  ```java
  // Create aggregate with relative node include for "nt:base"
  Aggregate agg = new Aggregate(mapper, "testAgg",
      ni("nt:base", "*", true));  // relativeNode = true
  
  // Build tree: testRoot/childNode (nt:base) with grandChild under it
  NodeState testRoot = builder("testRoot", 
      child("childNode", "nt:base",
          property("prop1", "val1"),
          child("grandChild", "nt:base",
              property("prop2", "val2"))));
  
  // Collect results from aggregate includes
  List<NodeIncludeResult> results = new ArrayList<>();
  for (Include include : agg.getIncludes()) {
      include.collectResults(testRoot, results);
  }
  
  // Should find 2 child nodes (childNode and grandChild), not just 1
  assertEquals(2, results.size());
  ```

- Incorrect example:
  ```java
  // WRONG: Only tests non-relative include (no relativeNode=true)
  Aggregate agg = new Aggregate(mapper, "testAgg",
      ni("nt:base", "*", false));  // relativeNode = false
  
  // WRONG: Flat tree with no depth
  NodeState testRoot = builder("testRoot", 
      child("childNode", "nt:base", property("prop1", "val1")));
  
  // Even if this passes, it doesn't catch the relativeNode bug
  // because the bug requires child nodes under the matched node
  ```