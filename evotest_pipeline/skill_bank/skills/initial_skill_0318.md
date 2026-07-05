---
name: wildcard-comment-handling
description: When parsing source code that contains wildcard characters (*, ?) inside
  comments, the parser may incorrectly interpret them as type-related tokens. This
  skill teaches how to test comment parsing robustness with wildcard-rich comment
  text to catch such bugs.
code_tags:
- COMPONENT_ADDITION_ID
- STATE_MUTATION
- VALIDATION
- WILDCARD_COMMENT_HANDLING
test_pattern: PARAMETRIC_TEST
---

# wildcard-comment-handling

## Instructions

# Wildcard Comment Handling

## Instructions

- WHEN the TG encounters a source code parser or comment extraction module that processes comments (inline comments, Javadoc, or block comments) containing special characters like `*` or `?`
- THEN it should write a test that:
  1. Creates or parses source code containing comments with wildcard characters (e.g., `/* some * wildcard ? text */`, `//?what?`, or multiline comments containing both `*` and `?`)
  2. Passes the source through the comment parsing/extraction logic
  3. Asserts that the comment text is correctly extracted or preserved without the parser throwing an exception or corrupting the comment content
  4. Asserts that wildcard characters in comments do NOT interfere with the parsing of adjacent code elements (e.g., type references, method signatures, annotations)
  5. If the comment parser is expected to handle `@param`, `@return`, or other Javadoc tags, ensure wildcard characters inside those tag descriptions do not break tag parsing

- Common pitfalls to avoid:
  - Testing only comments without wildcard characters — wildcard comment handling is a specific edge case
  - Testing only `//` single-line comments while ignoring `/* */` block comments and Javadoc `/** */` comments
  - Forgetting to test comments inside method bodies, not just class-level comments
  - Assuming the parser handles all special characters generically — wildcards (`*`, `?`) are often mistakenly treated as type parameter tokens by parser logic
  - Not testing that the wildcard text appears verbatim in the extracted output (the comment should not be modified or truncated)

- Example — Correct test approach:
  ```java
  // Create source with wildcard characters inside comments
  String source = "class Foo { /* test * wildcard ? character */ void bar() {} }";
  CtClass<?> ctClass = launcher.parseClass(source);
  // Extract first comment from the class
  List<CtComment> comments = ctClass.getComments();
  // Verify comment content contains the wildcard characters
  assertEquals(" test * wildcard ? character ", comments.get(0).getContent());
  ```

- Example — Incorrect test approach (too simplistic):
  ```java
  // BAD: No wildcard characters in comments
  String source = "class Foo { /* simple comment */ void bar() {} }";
  CtClass<?> ctClass = launcher.parseClass(source);
  // This test passes even if wildcard handling is broken
  ```