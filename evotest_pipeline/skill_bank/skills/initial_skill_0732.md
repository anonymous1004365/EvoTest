---
name: query-result-state-mutation-on-iterate
description: When a Query Result object may have its internal state mutated by calling
  getSize() during result iteration, the test should verify that getSize() returns
  the correct count before and/or after iteration, not just that iteration works.
  This skill applies to JCR/Jackrabbit query testing where result size is accessed
  alongside node iteration.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# query-result-state-mutation-on-iterate

## Instructions

# Test Query Result Size Correctness When Iterating Nodes

## Instructions

- WHEN testing a JCR `Query.execute().getNodes()` result where the test calls both `getSize()` on the `QueryResult` and iterates over the `RowIterator`/`NodeIterator`:
  - THEN the test must verify that `getSize()` returns the expected total hit count BEFORE or AFTER iteration, not just assume the iterator contains the right number of nodes.
  - THEN the test must verify that the `RowIterator` (or `NodeIterator`) returns the correct number of results matching the `getSize()` count.
  - Specifically, use `assertEquals(expectedSize, result.getSize())` and also count nodes via the iterator, checking both match.

- WHEN a query uses an index (e.g., a property index like `rep:estimatedSize` or `oak:index`) and the test modifies nodes (add/remove) before the query:
  - THEN the test must wait for async index updates to complete (e.g., `session.refresh(true)` or `Thread.sleep(long)` for indexing delay) before executing the query.
  - THEN the test must assert the exact expected number of hits, not just a non-zero count.

- WHEN a test calls `session.logout()` or modifies session state between query setup and result consumption:
  - THEN the test must capture (`result.getSize()`) and consume the results (iterate over nodes) BEFORE closing the session that created them, OR ensure the result's internal state is fully materialized.
  - Example: `long size = result.getSize();` followed by `RowIterator it = result.getRows(); int count = 0; while (it.hasNext()) { it.nextRow(); count++; } assertEquals(size, count);`

- Avoid common pitfalls:
  - ❌ Calling `result.getSize()` only and not verifying iterator count.
  - ❌ Calling `session.logout()` before accessing `result.getSize()` or iterating the result.
  - ❌ Assuming default session behavior applies without explicitly refreshing/updating after pending changes.
  - ❌ Testing only one property value (e.g., only `String` type) when the query indexes multiple types — test with all relevant types (e.g., both `String` and `Long` properties).

- Correct example pattern:
```java
// Correct: verify both getSize() and iterator count match
QueryResult result = query.execute();
long size = result.getSize();
RowIterator it = result.getRows();
int count = 0;
while (it.hasNext()) {
    it.nextRow();
    count++;
}
assertEquals("Total hits should match getSize()", size, count);
assertEquals("Expected exact number of hits", expectedHits, size);
```

- Incorrect example pattern:
```java
// Incorrect: only iterates, never validates getSize() — bug might be hidden
QueryResult result = query.execute();
RowIterator it = result.getRows();
int count = 0;
while (it.hasNext()) {
    it.nextRow();
    count++;
}
// No assertion on getSize() — could be wrong and test doesn't catch it
```