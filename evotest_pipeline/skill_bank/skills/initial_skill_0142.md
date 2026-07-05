---
name: xml-tokenizer-attribute-with-slash-handling
description: When testing the XML tokenizer (tokenizeXML), test with XML elements
  that contain a forward slash (/) inside attribute values. The tokenizer's regex
  pattern for matching self-closing tags can incorrectly match attribute content containing
  '/' as a self-closing tag boundary, causing the iterator to produce incomplete tokens.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# xml-tokenizer-attribute-with-slash-handling

## Instructions

# XML Tokenizer Attribute with Forward Slash Handling

## Instructions

**WHEN** the TG encounters code that uses `tokenizeXML("tagName")` to split XML content (via `TokenXMLExpressionIterator` or `ExpressionBuilder.tokenizeXMLExpression()`) — specifically the pattern where the regex `SCAN_BLOCK_TOKEN_REGEX_TEMPLATE` is compiled to match both self-closing tags `<tagName .../>` and block tags `<tagName>...</tagName>`:

- **THEN** the TG should test with XML elements whose attributes contain a forward slash `/` character, such as `<person attr='/' />`. The bug occurs because the regex pattern for self-closing tags (`<{0}(\\s+[^>]*)?/>`) uses `/>` as a delimiter, and a slash inside an attribute value can prematurely terminate the self-closing tag match.
- **THEN** the TG should verify that:
  - The complete element including the slash attribute is returned as a single split token (e.g., `"<person attr='/' />"`).
  - The number of split tokens matches the expected count (e.g., 1 token for a single self-closing element with a slash in an attribute).
  - Elements after the one containing the slash are also correctly tokenized.
- **THEN** the TG should expect that on the buggy version, the tokenizer incorrectly matches only a partial element (e.g., `<person attr='`) or produces the wrong number of tokens (e.g., 0 instead of 1), causing `MockEndpoint` assertions to fail with `Expected: <1> but was: <0>`.
- **Common pitfall**: Testing only with slash-free attributes (e.g., `<person name="Claus"/>`) or only with normal text content. The slash inside an attribute value (`attr='/'`) triggers the regex matching bug, while slashes in other positions may not.
- **Common pitfall**: Not testing self-closing tags that have a space before `/>` combined with a slash in an attribute (e.g., `<person attr='/' />` with a space before the self-closing `/>`).

**Correct test example** (catches the bug):
```java
public void testSplitTokenizerEWithSlash() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:split");
    String xml = "<persons><person attr='/' /></persons>";
    mock.expectedBodiesReceived("<person attr='/' />");
    template.sendBody("direct:e", xml);
    mock.assertIsSatisfied();
}
```

**Incorrect test example** (misses the bug):
```java
public void testSplitTokenizerE() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:split");
    mock.expectedBodiesReceived("<person>Claus</person>", "<person>James</person>", "<person>Willem</person>");
    String xml = "<persons><person>Claus</person><person>James</person><person>Willem</person></persons>";
    template.sendBody("direct:e", xml);
    assertMockEndpointsSatisfied();
}
```