---
name: javascript-line-comment-escaping
description: When testing a JavaScript comment/whitespace stripper, consider slash
  characters inside strings that resemble line comments (//). This skill teaches testing
  for escaped forward slashes inside string literals that should not trigger comment
  state transitions.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# javascript-line-comment-escaping

## Instructions

# JavaScript Line Comment Escaping Detection

## Instructions

- WHEN the TG encounters a `JavaScriptStripper` class (or similar JS comment stripping logic) that detects line comments using the pattern `c == '/' && next == '/' && prev != '\\'`
- THEN the TG should write tests that verify that a literal `//` sequence appearing inside a double-quoted or single-quoted string is NOT misinterpreted as a line comment start. Specifically:
  - Create test inputs that contain `"//"` (double-quoted string containing two forward slashes)
  - Create test inputs that contain `'//'` (single-quoted string containing two forward slashes)
  - Create test inputs that contain escaped forward slashes like `"\\//"` inside strings
  - Verify that the content inside the strings is preserved (not stripped) and the state machine does NOT transition to LINE_COMMENT state

- WHEN the TG is testing the `stripCommentsAndWhitespace(String original)` method of `JavaScriptStripper`
- THEN the TG should include test cases where `//` appears as a value inside string literals, not just as a comment. For example:
  - `"if ( !t.indexOf(\"//\") ) {"` — the `//` inside `\"//\"` should not be treated as a comment
  - `"replace(/^\\//i, \"\")"` — regex pattern containing escaped forward slashes
  - `"t.indexOf(\"//\")"` — the `//` inside a function argument string

- WHEN asserting the result of `stripCommentsAndWhitespace`
- THEN the TG should use `assertEquals` to compare against the expected output, where string literals containing `//` are preserved unchanged in the output
- Common pitfalls to avoid:
  - Testing only line comments starting with `//` at the start of a line (not inside strings)
  - Assuming that `prev != '\\'` check alone prevents all false positives — it only prevents escape sequences like `\\//` but NOT the case where `//` appears inside a string literal like `"//"`
  - Not including the quote characters around `//` in the test input, which is necessary to trigger the bug (the state machine must be inside STRING_DOUBLE_QUOTES or STRING_SINGLE_QUOTE state to avoid the false positive)
  - Forgetting that the stripper processes character-by-character with a state machine — the fix requires the state to be checked before deciding if `//` is a comment

### Correct Example
```java
@Test
public void unixWICKET501()
{
    String s = new JavaScriptStripper().stripCommentsAndWhitespace(
        "    // Handle the common XPath // expression\n" +
        "    if ( !t.indexOf(\"//\") ) {");
    assertEquals(" \n if ( !t.indexOf(\"//\") ) {", s);
}
```

### Incorrect Example (would pass buggy code)
```java
@Test
public void wrongTest()
{
    // This only tests simple line comments, not the interaction with strings containing //
    String s = new JavaScriptStripper().stripCommentsAndWhitespace(
        "    // this is a comment\n    foo()");
    assertEquals(" \nfoo()", s);
    // This test passes even on the buggy version, missing the real issue
}
```