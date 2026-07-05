---
name: full-text-filter-constraint-order
description: When testing queries with full-text constraints and additional filter
  conditions, the TG should verify the test exercises all filter planning logic paths
  — especially the interaction between full-text expressions and property constraints
  that can cause traversing indexes to yield zero results when they should return
  matches.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# full-text-filter-constraint-order

## Instructions

# Full-Text Filter Constraint Order Skill

## Instructions

WHEN the TG encounters a query that combines a `CONTAINS(...)` (full-text) constraint with additional filter conditions (e.g., property existence constraints, path restrictions) on a `QueryImpl` or `FilterImpl` object:

- THEN the TG should test the query end-to-end using `TraversingIndex` (which is used when no dedicated full-text index is available) to verify the full query execution returns correct results.
- The query engine processes constraints in a specific order, and the buggy code may skip or partially apply the full-text constraint when other constraints also exist on the filter. The fix may be in `FilterImpl.getFullTextConstraint()`, `FullTextSearchImpl.evaluate()`, or `QueryImpl` planning logic.
- WHEN the TG writes a test, it should:
  1. Create a repository (via `NodeStore` + `ContentRepository`) with nodes that would match the full-text term AND satisfy other filter conditions (e.g., property existence).
  2. Execute the query using `QueryImpl` or a standard `Query` API.
  3. Assert that the result set contains the expected node(s) — specifically **not** asserting `expected:<1> but was:<0>` (i.e., verify results are non-empty).
  4. If the query uses `getFullTextComparisonWithoutIndex()` (returned via `QueryEngineSettings`), set it to `true` to force the traversing index path.
- The TG should test **both** scenarios:
  - Full-text constraint alone (no other filter conditions)
  - Full-text constraint combined with property existence constraints on the same selector

- **Common pitfall**: Only testing the full-text constraint in isolation. The bug manifests specifically when a full-text constraint AND other filter conditions exist together. The traversing index's `isPotentiallySlow()` may return true for the combined case, triggering a different code path that mishandles the full-text term evaluation.

- **Common pitfall**: Mocking the `Filter` or `Query` objects instead of running an actual end-to-end query. The bug involves subtle interactions in query planning and constraint evaluation that mocks cannot reproduce. Use an in-memory Oak repository with actual content.

- **Example (correct test approach)**:
```java
// Create repository with content
ContentRepository repo = ...;
NodeStore store = ...;
// Add a node with property 'jcr:title' containing "hello"
// and also having a 'jcr:description' property (property existence condition)
// Execute query: SELECT * FROM [nt:base] WHERE CONTAINS(*, 'hello') AND jcr:description IS NOT NULL
// Assert result set size == 1
```

- **Example (incorrect test approach)**:
```java
// BAD: Only tests full-text alone, no property existence
// Query: SELECT * FROM [nt:base] WHERE CONTAINS(*, 'hello')
// This passes on buggy code too, missing the bug entirely
```

- The TG should ensure the test fails on the buggy version and passes on the fixed version by relying on the combined constraint scenario.