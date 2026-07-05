---
name: fulltext-parser-nested-parentheses-and
description: When testing a fulltext parser that handles AND/OR expressions separated
  by whitespace, test with parentheses-wrapped AND patterns like "(*)world" to verify
  nested group parsing doesn't crash. This skill applies to parsers that build expression
  trees from textual patterns.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- VALIDATION
- EDGE_CASE_INPUT
- ESCAPE_SEQUENCE_HANDLING
test_pattern: EXCEPTION_TEST
---

# fulltext-parser-nested-parentheses-and

## Instructions

# FullText Parser: Handling of Nested/Grouping Parentheses in AND Expressions

## Instructions

- WHEN the TG encounters a fulltext parser (such as `FullTextParser`) that parses space-separated AND terms from a string pattern
- THEN the TG should test with patterns containing **parentheses-wrapped unexpected characters** (e.g., `(*)world`) that might confuse the parser's term-splitting logic, verifying that a `ParseException` is thrown with a descriptive error message
- Specifically, when the parser's `parseAnd()` method is called after parsing a `Term`, if the remaining text starts with unexpected characters like `(*)`, the parser should raise `ParseException` containing `"; expected: term"` rather than silently accepting or crashing
- The TG should verify that the parser correctly advances its position and reports the exact syntax error location using the `(* )` marker notation in the error message

## Common Pitfalls

- Testing only well-formed patterns (e.g., "hello world", "hello OR world") and forgetting to test malformed or "orphaned" parentheses/grouping markers
- Assuming that after parsing one term, the remainder will always be a valid term — when it could be garbage characters like `(*)`
- Writing tests that only check `assertTrue`/`assertFalse` for evaluation results, without testing `ParseException` cases for invalid syntax
- Not verifying the exact error message format, which includes the position marker `(*)` and the expected token description

## Examples

### Correct Test (Use this approach)

```java
// Test that parser rejects malformed grouped/AND expressions
@Test
public void andWithGroupingMarkers() throws ParseException {
    // "(*)world" — after parsing the first term, the parser encounters "(*)"
    // which is not a valid term separator or term start
    try {
        FullTextParser.parse(null, "(*)world");
        fail("Expected ParseException");
    } catch (ParseException e) {
        String msg = e.getMessage();
        assertTrue(msg.startsWith("FullText expression: "));
        msg = msg.substring("FullText expression: ".length());
        assertEquals("(*); expected: term", msg);
    }
}
```

### Incorrect Test (Avoid this)

```java
// WRONG: Only testing valid AND expressions, missing the garbage-parentheses case
@Test
public void and() throws ParseException {
    assertEquals("\"hello\" \"world\"", convertPattern("hello world"));
    assertEquals("\"hello\" \"or\" \"world\"", convertPattern("hello or world"));
    assertTrue(test("hello world", "hello world"));
    // Missing test for patterns like "(*)world" that should throw ParseException
}
```

```java
// WRONG: Catching the exception without checking the detailed error message
@Test
public void andWithGroupingMarkers() {
    try {
        FullTextParser.parse(null, "(*)world");
        fail("Expected ParseException");
    } catch (ParseException e) {
        // OK but not thorough — doesn't verify the error message format
    }
}
```