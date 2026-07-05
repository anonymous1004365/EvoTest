---
name: empty-lucene-property-index-query
description: When a Lucene property index exists but has no indexed documents (empty
  index), querying it may throw NullPointerException. This skill teaches how to test
  that querying an empty Lucene property index returns zero results without throwing
  exceptions.
code_tags:
- EMPTY_INDEX_HANDLING
test_pattern: STATE_TEST
---

# empty-lucene-property-index-query

## Instructions

# Empty Lucene Property Index Query Handling

## Instructions

- WHEN the code under test creates a `LucenePropertyIndex` instance and an empty `IndexNode` (with no indexed Lucene documents) for a property restriction query
- THEN the test **must** verify that querying the empty index does not throw any exception (especially `NullPointerException`) and returns zero results
- The test should: (1) create a `NodeState` with a valid index definition node (e.g., using `IndexDefinitionBuilder` or `child(...)` to create `oak:index/luceneProperty` with `type` property `"lucene"` and `async` property `"async"`), (2) obtain the `LucenePropertyIndex` via `LucenePropertyIndexProvider` or similar infrastructure, (3) create a `Filter` with a `PropertyRestriction` (e.g., `jcr:uuid`), (4) call the index's `query(...)` method and collect results
- USE `assertNotNull` on the returned cursor and iterate over it to verify no `NullPointerException` occurs
- Common pitfall: only testing the index with actual data present; the bug manifests *only* when the index definition exists but the index contains no documents (i.e., empty index) — WITHOUT this test, a `NullPointerException` may be thrown inside the `LucenePropertyIndex` query path when it tries to create a `BooleanQuery.Builder` or access an `IndexSearcher` from an empty reader

Example (correct):
```java
// Verify that querying an empty Lucene property index returns results without NPE
NodeState root = createIndexDefinition(); // creates oak:index/luceneProperty definition
// No data is added, so index is empty
LucenePropertyIndex lpIndex = new LucenePropertyIndex();
NodeState indexState = NodeStateUtils.getNode(root, "/oak:index/luceneProperty");
Filter filter = createFilter(root, PropertyRestriction("jcr:uuid"));
Cursor cursor = lpIndex.query(filter, indexState);
assertNotNull(cursor);
// Iterate to trigger the NPE on buggy version
int count = 0;
while (cursor.hasNext()) {
    cursor.next();
    count++;
}
assertEquals(0, count);  // Expect zero results, no exception
```

Incorrect (fails to detect the bug):
```java
// Only test with non-empty index — does NOT exercise the empty-index code path
LucenePropertyIndex lpIndex = new LucenePropertyIndex();
// ... add documents to index first ...
Cursor cursor = lpIndex.query(filter, indexState);
assertTrue(cursor.hasNext());  // This test never fails because index is not empty
```