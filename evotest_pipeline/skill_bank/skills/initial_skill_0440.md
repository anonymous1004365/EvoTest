---
name: open-close-tag-expansion-void-element-filtering
description: When testing markup filters that expand open-close tags (OPEN_CLOSE →
  OPEN + CLOSE), verify that HTML void elements (e.g. br, hr, img, input) are NOT
  expanded but instead passed through unchanged. Teaches how to test that a tag processing
  pipeline correctly distinguishes expandable from non-expandable tags.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# open-close-tag-expansion-void-element-filtering

## Instructions

# Open-Close Tag Expansion: Filtering Out HTML Void Elements

## Instructions

- WHEN the TG encounters an `OpenCloseTagExpander` (or similar markup filter) that has a list of tags to expand (e.g., `REPLACE_FOR_TAGS` containing `"div"`, `"span"`, `"li"`, `"a"`, etc.) and a comment/whitelist of elements that should NOT be expanded (HTML void elements: `area`, `base`, `br`, `col`, `command`, `embed`, `hr`, `img`, `input`, `keygen`, `link`, `meta`, `param`, `source`, `track`, `wbr`)

- THEN the TG should write a **parametric test** that iterates over ALL HTML void elements and, for each one:
  1. Create a `ComponentTag` with that element name and `TagType.OPEN_CLOSE`
  2. Pass it through `onComponentTag()`
  3. Call `nextElement()` to get the next markup element out of the filter
  4. Assert that the returned element is **NOT** a `ComponentTag` closing the original tag (i.e., the void element was **not** split into OPEN + CLOSE)
  5. Verify that the `ComponentTag` type was **not changed** from `OPEN_CLOSE`

- WHEN the TG encounters the `OpenCloseTagExpander`'s expandable tags list (`REPLACE_FOR_TAGS`)

- THEN the TG should write a **counter-test** (or extend the parametric test) that iterates over ALL expandable tags and, for each one:
  1. Create a `ComponentTag` with that element name and `TagType.OPEN_CLOSE`
  2. Pass it through `onComponentTag()`
  3. Call `nextElement()` to retrieve the created closing tag
  4. Assert that the returned element **is** a `ComponentTag` whose `closes(tag)` returns `true` and whose name matches the original tag name

- **Common pitfalls**:
  - Testing only a subset of void elements or expandable tags instead of all of them
  - Forgetting that `OpenCloseTagExpander.nextElement()` returns the **closing** tag on the first call (after `onComponentTag` stored it), and the **next filter's** element on subsequent calls — the test must account for this queuing behavior
  - Not checking the `closes()` relationship between the generated closing tag and the original open tag
  - Not testing both void elements AND expandable elements to verify they behave oppositely

### Example (correct):

```java
// Test that void elements like <br/> are NOT expanded
@Test
public void doNotExpandVoidElements() throws ParseException {
    String[] htmlVoidElements = new String[] { "area", "base", "br", "col", "command", "embed",
            "hr", "img", "input", "keygen", "link", "meta", "param", "source", "track", "wbr" };
    for (String htmlVoidElement : htmlVoidElements) {
        OpenCloseTagExpander expander = new OpenCloseTagExpander() {
            @Override
            public IMarkupFilter getNextFilter() {
                return new AbstractMarkupFilter() {
                    @Override
                    protected MarkupElement onComponentTag(ComponentTag tag) { return null; }
                    @Override
                    public MarkupElement nextElement() throws ParseException {
                        return new TestMarkupElement(); // sentinel to detect pass-through
                    }
                };
            }
        };
        ComponentTag tag = new ComponentTag(htmlVoidElement, XmlTag.TagType.OPEN_CLOSE);
        expander.onComponentTag(tag);
        MarkupElement markupElement = expander.nextElement();
        // Should be the next filter's element, NOT a generated closing tag
        assertThat(markupElement, instanceOf(TestMarkupElement.class));
    }
}
```

### Example (incorrect — tests only one void element):

```java
// WRONG: only testing <br/> instead of all void elements
@Test
public void doNotExpandVoidElements() throws ParseException {
    // Missing: "area", "base", "col", "command", "embed", "hr", "img",
    // "input", "keygen", "link", "meta", "param", "source", "track", "wbr"
    // This would miss a bug where only certain elements are properly handled
    ComponentTag tag = new ComponentTag("br", XmlTag.TagType.OPEN_CLOSE);
    expander.onComponentTag(tag);
    // ...
}
```