---
name: invalid-xml-token-iterator-error-handling
description: WHEN testing XML token iterators that call .next() on invalid/malformed
  XML input, THEN the test must verify that the method throws an appropriate exception
  (e.g., RuntimeException or SAXException) rather than silently returning null or
  failing without error. This skill applies to token-based XML iteration via TokenXMLExpressionIterator
  and similar classes.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# invalid-xml-token-iterator-error-handling

## Instructions

# Invalid XML Token Iterator Error Handling

## Instructions

- WHEN the TG encounters a class that iterates over XML tokens using an iterator pattern (e.g., `TokenXMLExpressionIterator`, `XMLTokenExpressionIterator`) and the input XML may be invalid or malformed:
  - THEN the TG MUST write a test that passes *invalid/malformed XML* as input to the iterator.
  - The test MUST call `.next()` on the iterator and verify that it throws an exception (e.g., `RuntimeException`, or any exception indicating parse failure).
  - Do NOT test only with valid XML — the bug manifests specifically when the XML is malformed (e.g., mismatched tags, illegal characters, wrong encoding).
  - Common pitfall: assuming that the iterator gracefully returns `null` or an empty result for invalid XML. Instead, the iterator is expected to propagate the parse error.

- WHEN testing token extraction from malformed XML (e.g., using `XMLTokenExpressionIterator` with an XPath token expression on invalid XML):
  - THEN the TG must verify that the call to `extractToken()` or the iterator's `.next()` throws an exception, not just returns `null` or empty.
  - The test should use a String of malformed XML (e.g., `<root><element>...</root>` without closing tags, or mixing invalid byte sequences) as the input.

- WHEN setting up the test:
  - Construct a `TokenXMLExpressionIterator` or `XMLTokenExpressionIterator` with an XPath-like token expression (e.g., `//token`).
  - Pass invalid XML to the iterator (e.g., via a `InputStream` or `String` source).
  - Use `assertThrows` or a `try-catch` with `fail()` to assert that calling `next()` or `extractToken()` throws an exception.

- Common pitfalls to avoid:
  - ❌ Testing only with valid XML and assuming the iterator handles invalid XML gracefully.
  - ❌ Asserting that `.next()` returns `null` for invalid input — the correct behavior is to throw.
  - ❌ Forgetting to call `.next()` after constructing the iterator (the bug only manifests on the actual traversal/parsing step).

### Example (Correct):
```java
@Test
public void testExtractTokenWithInvalidXML() {
    String invalidXml = "<root><element>...</root>"; // missing closing tags or malformed
    XMLTokenExpressionIterator iterator = new XMLTokenExpressionIterator("//element", 'i');
    iterator.init(source(invalidXml));
    assertThrows(Exception.class, () -> iterator.next());
}
```

### Example (Incorrect — will NOT catch the bug):
```java
@Test
public void testExtractTokenWithInvalidXML() {
    String invalidXml = "<root><element>...</root>";
    XMLTokenExpressionIterator iterator = new XMLTokenExpressionIterator("//element", 'i');
    iterator.init(source(invalidXml));
    Object result = iterator.next();
    assertNull(result); // WRONG: the buggy code may throw, not return null
}
```