---
name: empty-suggest-no-content
description: Teach the TG to test Lucene suggestion queries when no content has been
  indexed, verifying that the suggestion result returns null rather than throwing
  an NPE or returning incorrect results.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# empty-suggest-no-content

## Instructions

# Empty Suggest Query with No Indexed Content

## Instructions

- WHEN the TG encounters Lucene suggestion query logic (e.g., `Query.JCR_SQL2` with a `suggest(...)` function) or any suggestion/indexing component that performs queries on indexed data
- THEN the TG should write a test that exercises the suggest query **when nothing has been indexed at all** — i.e., no nodes matching the queried node type exist in the repository, and no matching content has been added
- Specifically, the test must:
  1. Create a Lucene suggest index definition (e.g., with `createSuggestIndex("lucene-suggest", "nt:base", "jcr:title")` or similar) that has `useInSuggest=true` and `analyzed=true`
  2. **NOT** add any nodes that would match the indexed node type (e.g., do not add any nodes of type `nt:base` with the indexed property)
  3. Execute a suggest query via `QueryManager.createQuery(suggestQuery, Query.JCR_SQL2).execute()`
  4. Iterate the result `RowIterator` and extract the `"suggestion"` column value
  5. **Assert that the suggestion value is `null`** — use `assertNull("There shouldn't be any suggestion", value)` — NOT `assertNotNull`
- The critical point is: the test must verify the **empty/edge case behavior** where the suggest index exists but no content has been indexed. On the buggy version, this may throw a `NullPointerException` or return an unexpected value. The assertion should verify `null` (no suggestion) rather than expecting an exception.

- Common pitfalls to avoid:
  - ❌ **Mistake**: Testing only the "happy path" where content exists and suggestions are expected. Without an empty/no-content test, a bug where the suggest code fails when the Lucene index has no documents will be missed.
  - ❌ **Mistake**: Expecting an exception (e.g., `@Test(expected = ...)`) when the correct behavior is to return `null` gracefully — the code should handle the empty index without crashing.
  - ❌ **Mistake**: Adding dummy content before the suggest query, which would mask the empty-index bug.

- Example (correct approach):
  ```java
  // Create suggest index
  createSuggestIndex("lucene-suggest", "nt:base", "jcr:title", false, false);
  // Do NOT add any nodes — leave the index empty
  session.save();

  String suggQuery = "SELECT [rep:suggest()] FROM [nt:base] WHERE SUGGEST('test')";
  QueryManager queryManager = session.getWorkspace().getQueryManager();
  QueryResult result = queryManager.createQuery(suggQuery, Query.JCR_SQL2).execute();
  RowIterator rows = result.getRows();

  String value = null;
  while (rows.hasNext()) {
      Row firstRow = rows.nextRow();
      value = firstRow.getValue("suggestion").getString();
  }
  assertNull("There shouldn't be any suggestion with no indexed content", value);
  ```

- Example (incorrect approach — would miss the bug):
  ```java
  // BAD: Adds indexed content before query, so empty-index path is never tested
  createSuggestIndex("lucene-suggest", "nt:base", "jcr:title", false, false);
  root.addNode("myNode", "nt:base").setProperty("jcr:title", "test 1");
  session.save();
  // ... suggest query would now return a value, masking the bug
  ```