---
name: relative-property-query-filter-semantics
description: Teaches how to test that relative property queries (e.g., SELECT * FROM
  [nt:base] WHERE NAME() LIKE 'test%' AND name = 'test:testRoot/test2') are correctly
  filtered by the query engine, ensuring property restrictions on descendant nodes
  don't match ancestor nodes incorrectly.
code_tags:
- VALIDATION
- QUERY_FILTER_SEMANTICS
test_pattern: PARAMETRIC_TEST
---

# relative-property-query-filter-semantics

## Instructions

# Relative Property Query Filter Semantics

## Instructions

**WHEN** the TG encounters a query engine that evaluates multi-criteria queries involving relative property constraints (e.g., `SELECT * FROM [nt:base] WHERE NAME() LIKE 'test%' AND name = 'test:testRoot/test2'`), where one property filter (e.g., `NAME() LIKE 'test%'`) should restrict results by node name pattern and another (e.g., `name = 'some/path'`) should further restrict to nodes at a specific relative path:

- **THEN** the TG MUST construct test data with the following structure:
  1. A root node (e.g., `test:testRoot`) with a child node (e.g., `test2`) where the child node's path matches the relative property value (`test:testRoot/test2`).
  2. Additional sibling nodes under the same root (e.g., `test3`, `test4`) whose names do NOT match the relative path value but DO match the name filter pattern.
  3. Query nodes using `JCR_SQL2` syntax with both a `NAME() LIKE` filter and a property equals filter using a relative path value.
  4. Assert that the result set size equals **exactly 1** (the specific descendant node) — NOT the total count of all nodes matching the name pattern.

- **THEN** the TG MUST verify that the query engine does NOT incorrectly return sibling nodes (e.g., `test3`, `test4`) that match the name pattern but NOT the relative path property constraint.

- **Common pitfalls to avoid:**
  - Testing only with `NAME()` filters alone without combining with relative property path constraints — the bug only manifests when both filters are active simultaneously.
  - Testing only with absolute path property values (e.g., `/test:testRoot/test2`) — the bug specifically involves relative path property matching where the value equals a relative path like `test:testRoot/test2`.
  - Neglecting to create sibling nodes with names that match the name pattern — without these extra nodes, the result set size may appear correct by coincidence even on the buggy version.
  - Using `Assert.assertEquals(expected, actual)` without checking both the size and the contents of the result set — the buggy version may return correct-size results but wrong nodes.

**Example of correct test setup:**
```java
// Correct: Sets up a tree where only one descendant matches the relative path
// Creates root with multiple children, then queries with NAME() LIKE + relative path
Tree t1 = root.addChild("test:testRoot");
Tree t2 = t1.addChild("test2");  // matches name = 'test:testRoot/test2'
t1.addChild("test3");  // matches NAME() LIKE 'test%' but NOT the path
t1.addChild("test4");  // matches NAME() LIKE 'test%' but NOT the path

// Query: SELECT * FROM [nt:base] WHERE NAME() LIKE 'test%' AND name = 'test:testRoot/test2'
// Expected: 1 result (only test2), NOT 3 (test2, test3, test4)
assertQuery("SELECT * FROM [nt:base] AS t WHERE NAME(t) LIKE 'test%' AND t.name = 'test:testRoot/test2'",
    "traversingIndex", ImmutableList.of("test:testRoot/test2"));
```

**Example of INCORRECT test setup (would miss the bug):**
```java
// WRONG: Only creates the matching node, no sibling nodes to reveal the bug
Tree t1 = root.addChild("test:testRoot");
Tree t2 = t1.addChild("test2");

// This test passes even on buggy version because there's only one node
assertQuery("SELECT * FROM [nt:base] AS t WHERE NAME(t) LIKE 'test%' AND t.name = 'test:testRoot/test2'",
    "traversingIndex", ImmutableList.of("test:testRoot/test2"));
```