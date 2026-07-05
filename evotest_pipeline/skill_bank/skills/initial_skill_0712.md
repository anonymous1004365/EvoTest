---
name: dynamic-markup-non-closed-tag-handling
description: When testing HtmlHandler with dynamically loaded markup that contains
  non-close-requiring tags (like img or br), the TG should verify that stack-based
  tag balancing correctly handles tag closure tracking without throwing exceptions.
  This skill covers testing custom markup labels that load HTML at runtime.
code_tags:
- HTML_TAG_STACK_BALANCING
- DYNAMIC_MARKUP_LOADING
- WICKET_ID_FLAG_PROPAGATION
test_pattern: STATE_TEST
---

# dynamic-markup-non-closed-tag-handling

## Instructions

# Dynamic Markup Non-Closed Tag Handling

## Instructions

### WHEN the TG encounters a custom markup label component (extending Label or MarkupLabel) that loads HTML markup dynamically via StringResourceStream — and that markup contains self-closing or non-close-requiring tags such as `<img>`, `<br>`, `<input>`, `<hr>`, or `<meta>` — THEN:

1. **Create a test page** that uses the custom markup label in its `onInitialize()`, setting the HTML content (e.g., `setDefaultModel(Model.of(...))`) to a string containing **both self-closing tags AND subsequent content that could interfere with tag closure detection**.

2. **Use WicketTester** to render the page via `tester.executeTest(...)`, providing an expected output HTML file. The test should verify that the page renders without throwing any exception.

3. **Expect and verify** that `HtmlHandler` (or equivalent markup parser) does NOT throw a `WicketRuntimeException` with the message "Unable to find close tag for: ..." when processing non-close-requiring tags like `<img>` or `<br>`.

4. **Verify the `doesNotRequireCloseTag` map** in `HtmlHandler` includes common HTML void elements: `"br"`, `"img"`, `"input"`, `"hr"`, `"meta"`, `"link"`, `"area"`, `"base"`, `"col"`, `"embed"`, `"source"`, `"track"`, `"wbr"`, `"param"`, and `"p"`. The tag balancing logic in `HtmlHandler.handleCloseTag()` and `handleOpenTag()` must correctly skip looking for closing tags for these elements.

5. **Common Pitfall**: Testing ONLY simple markup that consists solely of non-closed tags (e.g., just `<img>`) without surrounding context. The bug manifests specifically when a non-close-requiring tag appears **before other tags** (like `<br>`) that the stack balancer might try to associate as its close tag. Test with a mixed sequence like: `<img src="x"><br>Some text<br>More text`.

6. **Another Common Pitfall**: Not testing with dynamically loaded markup at all. Static markup in template files (.html) may be processed differently by different markup parsers than the programmatic `StringResourceStream` path used by `WebMarkupContainer` or custom labels. Always include a dynamic-markup-loading scenario.

### Example (Correct — catches the bug):

```java
@Test
public void loadMarkupWithNonClosedTagsDynamically() throws Exception
{
    Page page = new DynamicMarkupPageWithNonClosedTags();
    tester.executeTest(HtmlHandlerTest.class, page, "DynamicMarkupPageWithNonClosedTags_expected.html");
}
```

Where `DynamicMarkupPageWithNonClosedTags` is a page that:
- Creates a `CustomMarkupLabel` (extending `org.apache.wicket.markup.html.basic.Label`)
- In `onInitialize()`, sets its model to a string like `"<img alt='logo' src='logo.png'><br>Some text<br>Some more text"`
- `CustomMarkupLabel` overrides `getMarkup()` to return `new StringResourceStream(getDefaultModelObjectAsString())`

### Incorrect (misses the bug):

```java
@Test
public void testJustImgTag() throws Exception
{
    // Only tests a single non-close-requiring tag without surrounding content
    // This would pass even in the buggy version because the stack balancer only 
    // fails when a non-close-requiring tag is followed by other tags
    Page page = new SingleImgPageWithDynamicMarkup();
    tester.startPage(page);
    // No assertion about exception — test passes but doesn't verify correct behavior
}
```

### Common Pitfalls to Avoid:

- **Pitfall: Testing only static template markup.** The `MarkupParser` path for `StringResourceStream` (dynamic markup) may exercise different code paths than the standard file-based markup parsing. Always test the dynamic loading path explicitly.
- **Pitfall: Not including expected output verification.** Use `tester.executeTest(..., expectedHtmlFile)` or explicit assertions to verify correct rendering, not just absence of exceptions.
- **Pitfall: Testing non-closed tags in isolation.** The Wicket `HtmlHandler` uses a stack-based approach where open/close tag pairs are tracked. Testing only lone `<img>` or `<br>` tags without subsequent content may not exercise the edge case where the stack incorrectly tries to close an `<img>` tag with a `<br>` tag.