---
name: hyphenated-fulltext-search
description: When full-text search queries contain hyphens (dashes), the Lucene index
  tokenizer may split terms on hyphens, causing queries for hyphenated phrases to
  fail. Test with terms like "hello-world" to ensure the query layer properly matches
  indexed content containing hyphens.
code_tags:
- COLLECTION_CONTENT
- VALIDATION
- TOKENIZER_HYPHEN_HANDLING
test_pattern: PARAMETRIC_TEST
---

# hyphenated-fulltext-search

## Instructions

# Hyphenated Full-Text Search Queries

## Instructions

- WHEN the code performs full-text search (e.g., CONTAINS, full-text queries) against a Lucene-based index and the search term may contain hyphens (dashes)
- THEN the test generator SHOULD create a parametric test that:
  - Indexes content with hyphens in the full-text property (e.g., a property `jcr:title` set to "hello-world" or similar hyphenated value)
  - Issues a CONTAINS query searching for the same hyphenated term (e.g., `CONTAINS([jcr:title], 'hello-world')`)
  - Verifies that the result set size matches the expected number of matching nodes, not zero
  - The test should fail on the buggy version where the Lucene analyzer's tokenizer splits the hyphenated term, causing no match
- WHEN testing full-text search with hyphens
- THEN also test with a simple non-hyphenated term (e.g., "hello") as a baseline to confirm indexing and querying work correctly otherwise
- Common pitfalls:
  - Testing only simple single-word search terms (e.g., "hello") — this passes even on the buggy version and misses the hyphenation bug
  - Using `LIKE` or property-exact-match queries instead of CONTAINS full-text queries — the bug is specific to full-text search tokenization
  - Testing only in-memory or simple indexes that don't use Lucene's tokenizers — the bug is tied to the production Lucene analyzer
  - Forgetting to add the test content to the index before querying — the test must set up proper indexing via the test framework

### Correct test approach (Java/JUnit example)

```java
@Test
public void containsDash() throws Exception {
    // Setup: add content with hyphenated full-text property
    String path = addNodeWithContent("hello-world");
    
    // Query using CONTAINS with hyphenated term
    String query = "SELECT * FROM [nt:base] WHERE CONTAINS([jcr:title], 'hello-world')";
    List<String> result = executeQuery(query, SQL2);
    
    // Expectation: should find the node
    assertThat(result, hasItem(path));
    assertEquals(1, result.size());
}
```

### Incorrect approach (would miss the bug)

```java
// WRONG: Only tests non-hyphenated single words — never catches the hyphenation bug
@Test
public void containsSimple() throws Exception {
    addNodeWithContent("hello");
    String query = "SELECT * FROM [nt:base] WHERE CONTAINS([jcr:title], 'hello')";
    List<String> result = executeQuery(query, SQL2);
    assertEquals(1, result.size());
}

// WRONG: Uses LIKE instead of CONTAINS — LIKE bypasses the full-text tokenizer
@Test
public void likeSearch() throws Exception {
    addNodeWithContent("hello-world");
    String query = "SELECT * FROM [nt:base] WHERE [jcr:title] LIKE '%hello-world%'";
    List<String> result = executeQuery(query, SQL2);
    assertEquals(1, result.size());
}
```