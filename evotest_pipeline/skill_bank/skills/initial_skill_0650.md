---
name: shared-state-mutation-on-property-index
description: A skill for detecting bugs where a property index query reuses a shared
  mutable result set (e.g. a PathCursor) across multiple search operations without
  resetting or isolating state per call, leading to incorrect query results. Apply
  this when testing property index query methods that iterate over a shared cursor
  or collection.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# shared-state-mutation-on-property-index

## Instructions

# Shared State Mutation on Property Index Query

## Instructions

- WHEN the TG encounters a method that queries a property index and returns results by iterating over a shared mutable cursor or collection (e.g., a `PathCursor`, `List`, or `Iterator` that is a field on the class)
- THEN the TG should test that performing TWO OR MORE consecutive queries with different parameters (e.g., different property values, different property names, or different node types) returns the CORRECT results for EACH query independently, and that results from the first query do NOT pollute or corrupt the results of the second query
- Include concrete tests such as:
  1. Query for property `"foo"` with value `"value1"`, then query for property `"foo"` with value `"value2"` on the same index instance, and verify the second query returns only nodes matching `"value2"`, not a union of both
  2. Query with a node type constraint first, then without it, and verify the second query's results are correct
  3. Query with a large result set first (to populate the shared state), then with a small/empty result set, and verify the second returns correctly (i.e., the shared state was properly reset)
- For tests that must pass on the buggy version and fail on the fixed version (or vice versa): the test should expect specific paths/results and fail with an assertion error (e.g., `assertNotNull`, `assertEquals` on result size, or specific path matching) when the shared state leaks across calls
- Common pitfalls to avoid:
  - Testing only a single query call — this will NOT catch state mutation bugs. The bug only manifests on the SECOND or subsequent query on the same instance
  - Creating a new index instance for each test case — the shared state must be reused across queries on the SAME instance
  - Testing only the same query parameters twice — the bug requires DIFFERENT query parameters that produce different result sets

**Correct example** (catches the bug):
```java
// Shared index instance — critical to catch state mutation
PropertyIndexQuery query = new PropertyIndexQuery(root, "myIndex");

// First query — populate shared cursor
Iterable<String> results1 = query.query("foo", "value1", null);
List<String> paths1 = ImmutableList.copyOf(results1);
assertFalse(paths1.isEmpty());

// Second query — DIFFERENT value, should return DIFFERENT set
Iterable<String> results2 = query.query("foo", "value2", null);
List<String> paths2 = ImmutableList.copyOf(results2);

// If shared cursor wasn't reset, paths2 might be polluted with paths1's data
assertFalse("Expected results for value2 to be non-empty", paths2.isEmpty());
// Verify paths2 does NOT contain paths from value1 (if they're mutually exclusive)
for (String p : paths1) {
    assertFalse("Result from value1 leaked into value2 query", paths2.contains(p));
}
```

**Incorrect example** (misses the bug):
```java
// New instance per query — won't catch shared state mutation
Iterable<String> results1 = new PropertyIndexQuery(root, "myIndex")
    .query("foo", "value1", null);
List<String> paths1 = ImmutableList.copyOf(results1);

Iterable<String> results2 = new PropertyIndexQuery(root, "myIndex")
    .query("foo", "value2", null);
List<String> paths2 = ImmutableList.copyOf(results2);
// BUG NOT CAUGHT: each query uses a fresh instance with fresh internal state
```

**Another correct example** (node type constraint re-use):
```java
PropertyIndexQuery query = new PropertyIndexQuery(root, "myIndex");

// Query with node type constraint
Set<String> withType = Sets.newHashSet(query.query("foo", "bar", "nt:base"));
assertFalse(withType.isEmpty());

// Query WITHOUT node type constraint on same instance
Set<String> withoutType = Sets.newHashSet(query.query("foo", "bar", null));
// If the node-type-filtered cursor leaks, withoutType may be incorrectly filtered
assertTrue("Without type constraint should have >= results than with constraint",
           withoutType.size() >= withType.size());
```