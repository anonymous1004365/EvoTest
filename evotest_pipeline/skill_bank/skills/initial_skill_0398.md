---
name: conditional-comment-link-rewriting
description: When a Wicket page template uses conditional comments (e.g., <!--[if
  IE]>) within a <wicket:link> container around <a> tags, the link URL rewriting may
  fail or produce incorrect output. Write tests that verify the rendered HTML for
  pages with conditional comments wrapping BookmarkablePageLink components inside
  wicket:link enclosures.
code_tags:
- CONDITIONAL_COMMENT_HANDLING
test_pattern: PARAMETRIC_TEST
---

# conditional-comment-link-rewriting

## Instructions

# Conditional Comment Link Rewriting

## Instructions

- WHEN the TG encounters a Wicket Page class (extending WebPage) that adds a BookmarkablePageLink inside a constructor, AND the corresponding HTML markup has `<wicket:link>` containing HTML conditional comments (`<!--[if ...]>`) that wrap `<a>` tags with `wicket:id` attributes
- THEN the TG MUST create a test that renders the page using `executeTest(PageClass.class, "ExpectedResultFile.html")` and compare against an expected HTML file, verifying that the conditional comment structure is preserved and the `href` attribute in the `<a>` tag is correctly rewritten (e.g., to `./org.apache.wicket.markup.html.basic.SimplePage_3`)
- Include an additional test that renders the page and asserts the response string contains the correct conditional comment blocks with the rewritten link URL — for example: `assertTrue(document.contains("<!--[if lt IE 5.1]>\\n    <a href=\\\"./org.apache.wicket.markup.html.basic.SimplePage_3\\\" wicket:id=\\\"link\\\">Link</a>\\n  <![endif]-->"))`
- Verify with MULTIPLE different conditional comment types (e.g., `[if IE]`, `[if IE 6]`, `[if gte IE 5.5]`, `[if lte IE 5.5999]`, `[if lt IE 5.1]`) to ensure all variants are correctly handled
- Common pitfall: Testing only standard non-conditional anchor rewriting without checking that conditional comment boundaries are preserved. Always include at least one conditional comment variant in the test.
- Common pitfall: Assuming the expected result file is correct without verifying it against actual rendered output on the fixed version. Run the test on the fixed version first to capture the correct expected output.

### Correct Example:
```java
// Test for SimplePage_12 which has conditional comments around links
@Test
public void renderHomePage_12() throws Exception
{
    executeTest(SimplePage_12.class, "SimplePageExpectedResult_12.html");
}
```

### Incorrect Example (missing conditional comment variants):
```java
// WRONG: Only tests a single conditional comment type
@Test
public void renderHomePage_12() throws Exception
{
    executeTest(SimplePage_12.class, "SimplePageExpectedResult_12.html");
    // Fails because expected file only has [if IE] but markup has [if IE 6], [if gte IE 5.5], etc.
}
```