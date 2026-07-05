---
name: fulltext-query-special-char-escaping
description: When executing fulltext search queries via Oak Lucene, special Lucene
  query syntax characters (such as '!' or other operators) in user-provided search
  strings must be properly escaped using QueryParserBase.escape() before being passed
  to QueryParser.parse(), otherwise they cause INVALID_SYNTAX_CANNOT_PARSE exceptions.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# fulltext-query-special-char-escaping

## Instructions

# Fulltext Query Special Character Escaping

## Instructions

WHEN the TG encounters a test for fulltext search/fulltext query methods that construct a Lucene QueryParser query string from user-provided input (e.g., constructing a query like `foo:bar` or `fulltext("text")`),

THEN the TG should:

1. Verify that special Lucene query syntax characters (`!`, `&&`, `||`, `:`, `(`, `)`, `{`, `}`, `[`, `]`, `^`, `"`, `~`, `*`, `?`, `\`, `/`, `+`, `-`) in the search term are properly escaped using `QueryParserBase.escape(value)` before being passed to `QueryParser.parse(...)`.
2. Write a test that calls the fulltext search method with a search string containing at least these problematic characters: `!` (exclamation mark) or `:` (colon) — because they are Lucene query syntax operators that break parsing.
3. Assert that when the buggy code is used (unescaped special chars), the query throws an exception with message containing `INVALID_SYNTAX_CANNOT_PARSE` or `Syntax Error, cannot parse`.
4. Assert that when the fixed code is used (properly escaped special chars), the query executes without throwing any exception.

Common pitfalls to avoid:
- Testing only normal alphanumeric search strings — this masks the bug because only special Lucene syntax characters trigger it.
- Wrapping the search term in quotes without also escaping the inner content — simple quoting does NOT protect against all special characters like `!` or `:`.
- Testing only at the Lucene `QueryParser.parse()` level — instead, test through the Oak abstraction layer (e.g., `LucenePropertyIndex.query(...)` or similiar fulltext query path) to ensure end-to-end escaping.

Correct example (for a test method `public void fulltextQueryWithSpecialChars()`):
```java
// This test calls the Oak-level fulltext query with a string containing '!'
// On buggy version, it throws INVALID_SYNTAX_CANNOT_PARSE
// On fixed version, it completes successfully
String specialCharQuery = "foo!";
PropertyStateLuceneQueryInfo query = ...; // or similar Oak query abstraction
Tree result = ...;
```

Incorrect example (will NOT catch the bug):
```java
// Only tests normal strings — special chars not covered
String normalQuery = "foobar";
// Only tests at low level with QueryParser directly
QueryParser parser = new QueryParser("field", analyzer);
parser.parse("foo!"); // may already be fine, but only Oak-level test catches real path
```