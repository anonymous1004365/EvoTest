---
name: fulltext-parse-null-token-validation
description: When testing query fulltext parsing with multiple tokens, verify that
  null and empty tokens in the query string are handled correctly — they should be
  filtered out rather than causing incorrect query serialization or matching issues.
  This skill is relevant when a query parser splits user input into tokens and constructs
  boolean query expressions.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# fulltext-parse-null-token-validation

## Instructions

# Fulltext Parse Null Token Validation

## Instructions

- WHEN the TG encounters a fulltext query parser that splits a user-provided string into tokens (e.g., via `String.split()` on whitespace) and constructs boolean query expressions (AND/OR) from those tokens
- THEN the TG should test with a query string that contains **consecutive whitespace** (multiple spaces, tabs, newlines) between tokens, which produces **empty/null tokens** after splitting. The test should call the parser method (e.g., `FullTextParser.parse("propertyName", "hallo  hello")` with double space) and verify that:
  - The parser does NOT produce a `FullTextTerm` with an empty/null string value (which would cause a `NullPointerException` or produce malformed query representations like `+(:fulltext:hallo :fulltext:hello) +text:{* TO *}` instead of the expected `[:fulltext:hallo :fulltext:hello]`)
  - Empty/null tokens are filtered out before constructing the fulltext expression
  - The resulting serialized query or tree representation does not contain unexpected operators (like combining contains with text search) that would change the query semantics
- Common Pitfalls:
  - Testing only with single-space separated tokens, which never produce empty tokens
  - Assuming `String.split()` trims whitespace automatically (it does NOT — consecutive separators produce empty strings)
  - Testing only correct/valid inputs and forgetting to test edge cases in tokenization
  - Only testing the parser independently without verifying the serialized query output (which reveals the incorrect behavior)

### Correct Example (parsing with double space should filter empty token):

```java
// Given a query like "hallo  hello" (double space), the parser should
// produce only two FullTextTerm nodes, not three (including an empty one)
FullTextExpression exp = FullTextParser.parse("", "hallo  hello");
// Expect no FullTextTerm with empty/null value
assertEquals("hallo", ((FullTextTerm)((FullTextOr)exp).getList().get(0)).getText());
assertEquals("hello", ((FullTextTerm)((FullTextOr)exp).getList().get(1)).getText());
// Or alternatively test the serialized form
// Should be: [:fulltext:hallo :fulltext:hello]
// NOT: [+(:fulltext:hallo :fulltext:hello) +text:{* TO *}]
```

### Incorrect Approach (only testing single-space):

```java
// This only tests the normal case and misses the edge case
FullTextExpression exp = FullTextParser.parse("", "hallo hello");
// Consecutive whitespace is never tested
// Empty/null token bug is not detected
```