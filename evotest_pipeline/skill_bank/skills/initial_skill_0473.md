---
name: wildcard-property-escaping-for-lucene-queries
description: When constructing Lucene query strings from property values that may
  contain wildcards, the TG should ensure that special characters are properly escaped
  to prevent syntax errors like ParseException. This skill applies to any code that
  interpolates user values into query expressions.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# wildcard-property-escaping-for-lucene-queries

## Instructions

# Wildcard Property Escaping for Lucene Queries

## Instructions

- WHEN the TG encounters code that builds a Lucene query string by interpolating property values (e.g., `path_exact:/test*`) without escaping wildcard or special characters (like `*`, `?`, `+`, `-`, `!`, `(`, `)`, `:`, `^`, `[`, `]`, `"`, `{`, `}`, `~`, `|`, `&`, `/`)
- THEN it should write a test that passes a value containing a wildcard character (e.g., `*`) to the query-building method and verify that the resulting query string is properly escaped using `QueryParserBase.escape()` or a similar sanitization mechanism
- The test should expect that the query executes without throwing a `org.apache.lucene.queryparser.classic.ParseException`. On the buggy version, a `ParseException` will be thrown with a message like `Cannot parse 'path_exact:/test*': Lexical error... Encountered: <EOF>`
- Common pitfalls: 
  - Testing only with plain string values that do not contain wildcards (will not reveal the bug)
  - Escaping only the `*` character but missing other special characters like `?` or `/`
  - Assuming values are already sanitized before reaching the query-building method without checking the full call chain

### Correct Example (test that catches the bug):

```java
@Test
public void testWildcardQuery() throws Exception {
    // Setup
    SolrQueryIndex index = ...;
    // Exercise with a value containing wildcard
    String path = "/test*";  // the * causes a ParseException if not escaped
    // Verify: should not throw ParseException
    String query = index.buildQuery(path);
    assertFalse("Query should contain escaped wildcard", query.contains("/test*"));
    // Or more specifically
    assertTrue("Query should escape * character", query.contains("\\*"));
}
```

### Incorrect Example (misses the bug):

```java
@Test
public void testSimplePathQuery() throws Exception {
    SolrQueryIndex index = ...;
    String path = "/test";  // No wildcard — this will pass even on buggy code
    String query = index.buildQuery(path);
    // Test passes on both buggy and fixed versions — useless for catching this bug
}
```