---
name: lucene-query-special-character-escaping
description: ''
code_tags:
- VALIDATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# lucene-query-special-character-escaping

## Instructions

# Lucene Query Special Character Escaping

## Instructions

- WHEN building a Lucene query string that includes property path values, user-provided text, or any string that may contain special characters (e.g., colons `:`, slashes `/`, backslashes `\`, parentheses `()`, exclamation marks `!`, `AND`, `OR`, `NOT`, `+`, `-`, `"`, `~`, `*`, `?`, `^`, `[`, `]`, `{`, `}`)
- THEN the test MUST include at least one test case where the search string contains a colon (`:`) character: e.g., `"stockphotography\\:business/business_abstract"` as a fulltext query value, and verify that the query executes without throwing an `org.apache.lucene.queryparser.classic.ParseException` (or any `SyntaxError`).
- WHEN the codebase uses Lucene's `QueryParser.parse()` on a string built from user input or node property paths
- THEN verify that the test passes on the fixed version and fails on the buggy version with `INVALID_SYNTAX_CANNOT_PARSE` or a `ParseException` containing `Lexical error` or `Syntax Error, cannot parse`.
- WHEN constructing the test, use realistic values that mimic actual property paths (e.g., `"jcr:title/my-title"`, `"nt:base/node-type"`) rather than abstract placeholders.
- Avoid testing only with plain strings that have no special characters.
- Include at least one test where the special character appears in the middle of the query string (not just at the end), as colons and slashes embedded in path-like strings are the most common source of this bug.
- Verify that escaping is applied to the query string BEFORE it reaches `QueryParser.parse()`, not after.

### Common Pitfalls

- **Testing only with alphanumeric strings**: A test that only passes `"hello world"` or `"business_abstract"` will NOT catch this bug. The colon (`:`) character is the key trigger.
- **Escaping only at the end of the string**: The bug manifests when special characters appear in the middle of the query value (e.g., `"stockphotography\\:business/business_abstract"`), not just at boundaries.
- **Not checking the exception type**: The bug throws `ParseException` during query parsing. The test should either expect no exception (in a fixed version) or assert the specific exception and its `INVALID_SYNTAX_CANNOT_PARSE` message (in a buggy version).
- **Using `QueryUtils` escaping inconsistently**: If the codebase has its own escaping utility, test that it is called on the full query string, not just on individual tokens.

### Examples

**Correct** (Catches this bug):
```java
// Tests that fulltext queries with special characters (colon) don't cause parse errors
@Test
public void fulltextQueryWithSpecialChars() throws Exception {
    // This string contains a colon (:) and a slash (/) which trigger the bug
    String query = "stockphotography\\:business/business_abstract";
    
    // Should execute without ParseException
    List<Row> result = executeQuery(query, "lucene");
    
    assertNotNull(result);
    // Verify results are returned correctly
}
```

**Incorrect** (Does NOT catch this bug):
```java
@Test
public void fulltextQueryTest() throws Exception {
    // Only uses plain text without special Lucene syntax characters
    String query = "business_abstract";
    
    // This would pass even on the buggy version
    List<Row> result = executeQuery(query, "lucene");
    assertNotNull(result);
}
```

**Also Incorrect** (Escapes the wrong thing / incomplete):
```java
@Test 
public void fulltextQueryTest() throws Exception {
    // Escapes only some characters but not enough
    String query = "nt:base";  // Colon present but may be handled differently
    
    // Test passes but doesn't catch the path-like pattern with slash AND colon
    List<Row> result = executeQuery(query, "lucene");
}
```