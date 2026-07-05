---
name: multi-phrase-query-indexing-testing
description: When index or query logic constructs a MultiPhraseQuery from concatenated/aggregated
  terms, the test must verify that all terms produce correct query results. This skill
  guides testing of multi-term phrase query construction where terms may be dropped
  or mis-handled.
code_tags:
- MULTI_PHRASE_QUERY_INDEXING
- FULLTEXT_CHARACTER_FILTERING
- CONDITIONAL_BRANCH
test_pattern: PARAMETRIC_TEST
---

# multi-phrase-query-indexing-testing

## Instructions

# MultiPhraseQuery Indexing Testing

## Instructions

- WHEN the TG encounters code that indexes or queries by constructing a MultiPhraseQuery (e.g., using `MultiPhraseQuery.Builder` or calling methods like `multiPhraseQuery()`) — especially when terms are built by concatenating or iterating over collections of tokens/terms
- THEN the TG should write a test that:
  1. Indexes documents containing multiple distinct terms that should match the same phrase query position (e.g., both "foo" and "bar" as alternatives)
  2. Executes a MultiPhraseQuery that expects **all** of those terms to match
  3. Asserts that the query returns the expected documents — specifically verifying that **both** terms produce matches, not just one
  4. Uses `assertFalse(queryResult.isEmpty())` or similar to confirm results exist
- Common pitfalls:
  - Testing only a single term in a MultiPhraseQuery, which would not catch the bug where additional terms are silently dropped
  - Testing the query builder/API in isolation without actually indexing documents and running queries against an index
  - Using only string-typed terms without verifying that non-string terms (e.g., CtTypeReference, custom objects) are also correctly indexed
  - Assuming that if the query runs without exception, it produces correct results

### Example (Correct)

```java
// Correct: Index documents with multiple terms, query all of them
@Test
public void testMultiPhraseQueryWithMultipleTerms() throws Exception {
    // Index documents
    index("document1", "foo bar baz");
    index("document2", "foo qux baz");
    index("document3", "bar baz");
    
    // Create MultiPhraseQuery with both "foo" and "bar" as alternatives
    MultiPhraseQuery query = new MultiPhraseQuery.Builder()
        .add(new Term[] { new Term("field", "foo"), new Term("field", "bar") })
        .build();
    
    // Execute query
    TopDocs results = searcher.search(query, 10);
    
    // Assert both terms produce results — don't just check one
    assertTrue("Query should return matches for both 'foo' and 'bar' terms", 
               results.totalHits.value > 0);
    assertTrue("Should find document1 with both terms", 
               results.totalHits.value >= 2);
}
```

### Example (Incorrect)

```java
// Incorrect: Only tests a single term — won't catch dropped terms
@Test
public void testMultiPhraseQuery() throws Exception {
    index("document", "foo bar");
    
    // Only testing with one term — bug may silently ignore additional terms
    MultiPhraseQuery query = new MultiPhraseQuery.Builder()
        .add(new Term("field", "foo"))
        .build();
    
    // This passes even if multi-term logic is broken
    assertNotNull(searcher.search(query, 10));
}
```