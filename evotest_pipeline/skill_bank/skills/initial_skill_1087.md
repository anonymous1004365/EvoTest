---
name: lucene-special-chars-fulltext-query
description: When testing Lucene full-text queries that contain special characters
  (like hyphens, asterisks, question marks), the TG should verify these queries return
  expected results. Special characters in query strings may not be handled correctly
  by the query analyzer.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- SPECIAL_CHARS_LUCENE_QUERY
test_pattern: PARAMETRIC_TEST
---

# lucene-special-chars-fulltext-query

## Instructions

# Lucene Special Characters in Full-Text Queries

## Instructions

- WHEN the TG encounters a Lucene full-text search/property index (such as `LucenePropertyIndex`) that processes query strings containing special characters (e.g., hyphens `-`, asterisks `*`, question marks `?`, plus signs `+`, exclamation marks `!`, parentheses `()`, colons `:`)
- THEN the TG should write a test that:
  1. Creates indexed content where a property value contains special characters (e.g., `"test-fulltext"` with a hyphen)
  2. Performs a full-text query using a query string with those same special characters (e.g., `"test-fulltext"` as the query)
  3. Verifies that the query correctly matches the indexed document
  4. Expects that the query returns the correct path(s); on the buggy version, the query may return no results (empty list) when special characters are present in the query string

- Common pitfalls to avoid:
  - Testing only queries without special characters and assuming full-text search works the same for all inputs
  - Assuming Lucene's query parser correctly handles all special characters in query strings without explicit escaping or analysis
  - Only testing simple alphanumeric queries when the codebase contains property values with hyphens or other Lucene special syntax characters
  - Using `contains`-type queries instead of full-text queries that go through query analysis

- Example test pattern (correct):
```java
// Correct: Tests a full-text query with a hyphenated search term
String query = "test-fulltext";
Result result = queryResult(query, SQL2);
assertNotNull(result); // Should find the indexed document
```

- Example test pattern (incorrect):
```java
// Incorrect: Only tests alphanumeric queries, missing the special characters case
String query = "test fulltext";
Result result = queryResult(query, SQL2);
// Never tests "test-fulltext" which may behave differently
```