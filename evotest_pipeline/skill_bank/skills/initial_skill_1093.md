---
name: union-query-limit-offset-subquery-applied-once
description: When testing UNION queries with ORDER BY, LIMIT, and OFFSET, verify that
  the final result respects the offset, not just the limit. The bug was that UnionQueryImpl.applyLimitOffset()
  pushed limit+offset to subqueries but did not apply the offset itself, so offset
  was missing from final results.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# union-query-limit-offset-subquery-applied-once

## Instructions

# Union Query LIMIT/OFFSET Subquery Propagation

## Instructions

WHEN the TG encounters a UNION or UNION ALL query implementation that pushes LIMIT and OFFSET values into subqueries (e.g., via a method like `applyLimitOffset()` that computes `saturatedAdd(limit, offset)` and calls `left.setLimit(...)` and `right.setLimit(...)`):

- THEN the TG should verify that when both LIMIT and OFFSET are set on a UNION query, the final result respects the offset. Do not assume that pushing `limit + offset` to subqueries automatically applies the offset — the outer query must also skip the first `offset` rows.

- Specifically, the TG should test with a UNION query that:
  1. Returns multiple rows from each side (e.g., using SELECT with ORDER BY [jcr:path])
  2. Has a non-zero OFFSET (e.g., `OFFET 2`)
  3. Has a LIMIT that when added to OFFSET still produces results (e.g., `LIMIT 3, OFFET 2` — expecting 3 rows starting from position 2)
  4. Expect the total count of returned rows to equal the LIMIT value, not `limit + offset` and not some smaller value

- In the buggy version, the `UnionQueryImpl.applyLimitOffset()` method only calls `left.setLimit(subqueryLimit)` and `right.setLimit(subqueryLimit)` where `subqueryLimit = limit + offset`, but does NOT call `left.setOffset(...)` or `right.setOffset(...)` or apply the offset at the union level. This means the offset is effectively ignored — the union returns rows starting from index 0, not from the offset.

- The test should assert:
  - The number of result rows equals the LIMIT value (e.g., 3)
  - Each result row has the expected path (e.g., indexing into the full ordered list starting at the offset position)

- Common pitfalls to avoid:
  - Testing only LIMIT without OFFSET (this would not detect the bug)
  - Testing only OFFSET without LIMIT (the offset might still be broken)
  - Testing UNION queries without ORDER BY (offset/limit behavior depends on ordering)
  - Assuming that setting limit to `limit + offset` on subqueries automatically handles offset — the offset requires explicit handling, either by setting offset on subqueries or by skipping rows at the union level
  - Using the same query for left and right sides of the union — this is fine and can actually help reproduce ordering issues

### Example (correct test approach):

```java
// Setup data
Tree t = root.getTree("/").addChild("UnionQueryTest");
t = t.addChild("a");
t = t.addChild("b");
t = t.addChild("c");
t = t.addChild("d");
t = t.addChild("e");
root.commit();

// Execute UNION with ORDER BY, LIMIT, and OFFSET
String left = "SELECT [jcr:path] FROM [nt:base] AS a WHERE ISDESCENDANTNODE(a, '/UnionQueryTest')";
String right = "SELECT [jcr:path] FROM [nt:base] AS a WHERE ISDESCENDANTNODE(a, '/UnionQueryTest')";
String order = "ORDER BY [jcr:path]";
String union = String.format("%s UNION %s %s", left, right, order);

int limit = 3;
int offset = 2;

Result result = qe.executeQuery(union, QueryEngineImpl.SQL2, limit, offset,
        QueryEngine.NO_BINDINGS, QueryEngine.NO_MAPPINGS);

List<ResultRow> rows = Lists.newArrayList(result.getRows());

// Expected: rows starting from index 'offset' in the sorted full result
String[] expected = {
    "/UnionQueryTest/a/b/c",     
    "/UnionQueryTest/a/b/c/d",   
    "/UnionQueryTest/a/b/c/d/e"  
};

assertEquals(expected.length, rows.size());
int i = 0;
for (ResultRow rr : result.getRows()) {
    assertEquals(expected[i++], rr.getPath());
}
```

### Example (incorrect test approach — would not catch the bug):

```java
// BAD: Testing only limit without offset
Result result = qe.executeQuery(union, QueryEngineImpl.SQL2, 3, 0, ...);
// This passes even in buggy version because offset=0 is a no-op

// BAD: Testing only offset without limit
Result result = qe.executeQuery(union, QueryEngineImpl.SQL2, Long.MAX_VALUE, 2, ...);
// Might not detect the bug depending on implementation

// BAD: Not checking individual row paths, only count
Result result = qe.executeQuery(union, QueryEngineImpl.SQL2, 3, 2, ...);
assertEquals(3, Lists.newArrayList(result.getRows()).size());
// Count alone doesn't prove offset was applied — wrong rows could be returned
```