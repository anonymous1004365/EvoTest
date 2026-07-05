---
name: html-comment-strip-handling-in-markup-parser
description: When parsing HTML markup, comments that overlap with Wicket-specific
  tags or have specific markup-like content can cause parse failures. This skill helps
  the TG write tests that verify correct handling of HTML comments during markup parsing,
  especially when strip-comments settings or Wicket tag identification is involved.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# html-comment-strip-handling-in-markup-parser

## Instructions

# HTML Comment Strip Handling in Markup Parser

## Instructions

- WHEN the TG encounters HTML markup parsing code that processes HTML comments (e.g., `<!-- ... -->` inside Wicket markup templates)
- THEN the TG should write a test that:
  1. Creates markup content containing HTML comments that could trigger a `NullPointerException` or `StringIndexOutOfBoundsException` during parsing
  2. Tests with specific comment content that includes Wicket tag-like syntax (e.g., `<!-- <wicket:panel> -->`, `<!-- <wicket:extend> -->`)
  3. Tests with multiline HTML comments, comments nested inside other markup structures, or comments adjacent to Wicket component tags
  4. Calls `MarkupParser.parse()` (or equivalent) on the markup string and expects it to complete without throwing an exception
  5. Verifies that the parsed result correctly strips or preserves comments according to the markup settings

- **What to verify**: The test should assert that parsing HTML markup with comments does NOT throw `NullPointerException` or `StringIndexOutOfBoundsException`. The bug manifests as a crash during parsing when comment content interacts poorly with tag identification logic.

- **Common pitfalls to avoid**:
  - Testing only well-formed comments with no Wicket-specific content — the bug is triggered by specific comment content patterns
  - Testing only single-line comments — the bug may involve multiline or multi-tag comment structures
  - Testing only in `stripComments=true` mode without trying `stripComments=false` mode
  - Assuming comments are always independent of tag identification logic — the bug arises from interaction between comment processing and tag identification

- **Correct example**:
  ```java
  @Test
  public void testComments()
  {
    // Create markup with HTML comments that have Wicket-tag-like content
    MarkupParser parser = new MarkupParser(new MarkupResourceStream(
      new StringResourceStream("<html><body><!-- <wicket:panel> --><div wicket:id=\"test\">content</div><!-- </wicket:panel> --></body></html>",
      "text/html")));
    // Must not throw NullPointerException
    Markup markup = parser.parse();
    assertNotNull(markup);
  }
  ```

- **Incorrect example** (missing the specific comment content pattern that triggers the bug):
  ```java
  @Test
  public void testComments_trivial()
  {
    // Testing only trivial comments — won't catch the bug
    MarkupParser parser = new MarkupParser(new MarkupResourceStream(
      new StringResourceStream("<html><body><!-- simple comment --><div>content</div></body></html>",
      "text/html")));
    Markup markup = parser.parse();
    assertNotNull(markup);
  }
  ```