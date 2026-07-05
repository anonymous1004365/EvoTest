---
name: tag-attribute-put-escape
description: WHEN overriding onComponentTag with tag.put(key, value) to add custom
  attributes to a ComponentTag, THEN test that the value is not double-escaped. This
  skill catches double-escaping bugs where values added via tag.put() get an additional
  HTML-encoding pass on top of already-escaped attribute values.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# tag-attribute-put-escape

## Instructions

# Tag attribute put() escaping

## Instructions

WHEN the TG encounters code that calls `tag.put(String key, CharSequence value)` on a `ComponentTag` object inside an `onComponentTag(ComponentTag tag)` override, THEN the TG should write a test that verifies that the attribute value rendered in the final markup is not double-escaped.

Specifically:
- The TG should create a test page with markup that contains an HTML entity in a wicket-enabled tag attribute (e.g., `onclick="alert('alerting: &amp;')"`).
- In the Java component class, override `onComponentTag(ComponentTag tag)` and call `tag.put("some_attribute", "a & b")` — a raw ampersand value that should be single-escaped to `&amp;` in the final output.
- Start the page with `tester.startPage(TestPage.class)` and assert that the response contains `"some_attribute=\"a &amp; b\""`.
- Also assert that the HTML entities already present in the markup (like `&amp;` and `&pound;`) remain correctly rendered and are NOT double-escaped (e.g., check `response.contains("\u00a3\u00a3")` for pound entities, and `response.contains("&gt;&gt;")` for the `&gt;` entity without double-escaping).
- Use `assertTrue("meaningful message", response.contains("expected string"))` for assertions.

Common pitfalls to avoid:
- Testing only with simple alphanumeric values that don't trigger escaping (like `tag.put("foo", "bar")`). These pass even with double-escaping bugs.
- Failing to include both: (a) markup-declared HTML entities (to catch breakage of markup parsing) AND (b) a programmatically added attribute with an ampersand (to catch double-escaping of the put value).
- Forgetting to use `tester.getLastResponseAsString()` to capture the rendered output.
- Testing for `"a &amp; b"` inside an attribute incorrectly — you must match the full attribute syntax like `some_attribute="a &amp; b"`.

### Correct Example

```java
public class ButtonValuePage extends WebPage implements IMarkupResourceStreamProvider {
    public ButtonValuePage() {
        add(new Link<Void>("link") {
            @Override
            public void onClick() {}

            @Override
            protected void onComponentTag(ComponentTag tag) {
                super.onComponentTag(tag);
                tag.put("some_attribute", "a & b");
            }
        });
    }

    @Override
    public IResourceStream getMarkupResourceStream(MarkupContainer container, Class<?> containerClass) {
        return new StringResourceStream(
            "<html><body>" +
            "<a wicket:id=\"link\" onclick=\"alert('alerting: &amp; &pound;&#163; ')\">link</a>" +
            "</body></html>");
    }
}

@Test
public void componentAttributesNotDoubleEscaped() throws Exception {
    tester.startPage(ButtonValuePage.class);
    String response = tester.getLastResponseAsString();
    assertTrue("must not be double escaped", response.contains("Watch escaped value: &gt;&gt;"));
    assertTrue("escape manually added attributes", response.contains("some_attribute=\"a &amp; b\""));
}
```

### Incorrect Example

```java
// BAD: using a simple value that won't expose double-escaping
public ButtonValuePage() {
    add(new Link<Void>("link") {
        @Override
        public void onClick() {}

        @Override
        protected void onComponentTag(ComponentTag tag) {
            super.onComponentTag(tag);
            tag.put("some_attribute", "simpleValue"); // no ampersand — won't catch the bug!
        }
    });
}
```