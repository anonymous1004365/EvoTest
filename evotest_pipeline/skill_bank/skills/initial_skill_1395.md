---
name: chinese-text-tokenization-validation
description: When indexing or querying with CJK (Chinese/Japanese/Korean) text, test
  that multi-character Chinese words are properly tokenized and matchable. This skill
  helps catch tokenizer or analyzer configurations that fail to correctly segment
  CJK text, causing missing search results.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# chinese-text-tokenization-validation

## Instructions

# Chinese Text Tokenization Validation

## Instructions

- WHEN the TG encounters a Lucene/Solr index configuration, analyzer setup, or query processing that handles text for indexing or searching
- THEN it should verify that Chinese (CJK) multi-character terms are correctly tokenized and produce search matches, by adding a test that:
  1. Creates or indexes a node/property containing at least one multi-token non-ASCII word or phrase (for example, accented or CJK-like search terms represented in the fixture)
  2. Executes a query that searches for that exact Chinese term
  3. Asserts that the result set contains exactly 1 matching document
  4. The test should expect failure (empty result set) on the buggy version and success (1 result) on the fixed version

- WHEN testing CJK tokenization behavior
- THEN the test should use multi-character search terms that would be affected by tokenization issues, not single-character terms which would not expose the bug

- Common pitfalls to avoid:
  - Testing only single-character terms which would not reveal tokenization aggregation bugs
  - Testing only Latin/ASCII text tokenization — CJK tokenization often uses different analyzers
  - Using Unicode escapes instead of actual Chinese characters, which may hide encoding issues
  - Testing only the indexing side without verifying search queries can find the indexed content

### Example (correct approach, Java/JUnit):
```java
// Correct: tests CJK multi-character tokenization end-to-end
@Test
public void testTokenizeCN() throws Exception {
    // Index a node with a Chinese property value
    String idxName = ...; // setup index
    // add node with jcr:title="multiTokenTerm" or similar
    
    // Query for the Chinese term
    String query = "SELECT * FROM [nt:base] WHERE CONTAINS(*, 'multiTokenTerm')";
    
    // Verify the query returns matching results
    assertThat(queryResult.size(), is(1));
}
```

### Example (incorrect approach):
```java
// WRONG: single-character terms don't expose tokenization bugs
@Test
public void testChineseSearch() throws Exception {
    // A single-character term will not catch multi-character tokenization issues
    index("myProp", "x");
    assertThat(search("x").size(), is(1));
}

// WRONG: only testing Latin text misses CJK-specific analyzer behavior
@Test
public void testSearch() throws Exception {
    index("myProp", "hello world");
    assertThat(search("hello").size(), is(1)); // This works even with broken CJK tokenizer
}
```