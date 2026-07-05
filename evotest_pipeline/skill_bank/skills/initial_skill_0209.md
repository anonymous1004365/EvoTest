---
name: ajax-form-submit-javascript-escape
description: When testing Ajax form submit behaviors with JavaScript event handlers,
  ensure that JavaScript values containing special characters (like apostrophes) are
  properly escaped to prevent syntax errors. The TG should test that JavaScript event
  strings with apostrophes are correctly escaped in the generated HTML.
code_tags:
- ARGUMENT_VALIDATION
- EDGE_CASE_INPUT
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# ajax-form-submit-javascript-escape

## Instructions

# Ajax Form Submit JavaScript Escape

## Instructions

WHEN the TG encounters Ajax form submit behavior code that generates JavaScript event handler attributes (e.g., `onchange`, `onsubmit`) using user-provided JavaScript strings:

- THEN it should test with JavaScript strings that contain apostrophes/single quotes (`'`) to ensure proper escaping
- The test should verify that the generated attribute value does NOT contain an unescaped apostrophe that would break JavaScript syntax
- Specifically check that apostrophes in JavaScript event code are escaped as `\'` or that the JavaScript string uses a different quoting strategy
- Verify that no JavaScript syntax error would occur when the generated HTML attribute is evaluated by a browser

Common pitfalls to avoid:
- Testing only with simple alphanumeric JavaScript strings that don't exercise escaping paths
- Verifying only that the behavior fires correctly without checking the generated HTML attribute values
- Assuming that because the server-side code works, the client-side JavaScript will also work with special characters

Example of a correct test:
```java
@Test
public void testEventJavaScriptEscaped() throws Exception
{
    tester.startPage(AjaxFormSubmitTestPage.class);
    tester.clickLink("link");
    // The JavaScript event code contains an apostrophe that must be escaped
    // Expected: the rendered HTML properly escapes the apostrophe
}
```

The test should verify that:
- The generated page HTML contains the properly escaped JavaScript
- No JavaScript syntax error occurs due to unescaped characters in event handler attribute values