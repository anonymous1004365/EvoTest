---
name: xml-stream-reader-closing
description: When converting XMLStreamReader to other formats (like BufferedReader),
  the XMLStreamReader must be explicitly closed after reading to release underlying
  resources. Test that wrapped streams close the original reader properly.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# xml-stream-reader-closing

## Instructions

# XMLStreamReader Resource Closing in Stream Conversions

## Instructions

**WHEN** the TG encounters code that wraps an `XMLStreamReader` (or similar XML event reader) into another stream type (e.g., `BufferedReader`, `InputStream`, `Reader`), **THEN** the TG should:

1. **Test that the wrapper stream properly delegates close() to the underlying XMLStreamReader.** Create a mock or spy of `XMLStreamReader`, pass it to the conversion method, call `close()` on the returned stream, and verify that `XMLStreamReader.close()` was invoked.

2. **Test the resource leak scenario with a try-with-resources block.** Create a test where:
   - A valid XML string/input is provided
   - An `XMLStreamReader` is created from it (e.g., via `XMLInputFactory.createXMLStreamReader(...)`)
   - The reader is passed to the conversion method (e.g., `StaxConverter.toBufferedReader(xmlStreamReader)`)
   - The returned stream is wrapped in a try-with-resources
   - After the try-with-resources exits, verify that `xmlStreamReader.hasNext()` throws an `XMLStreamException` (indicating the reader was closed) — or use a spy to verify `close()` was called

3. **Test that encoding/charset is preserved.** If the conversion method reads the encoding from the `XMLStreamReader` (e.g., `xmlStreamReader.getEncoding()`), verify that:
   - The encoding is correctly obtained and applied
   - If `getEncoding()` returns `null` (which it does for non-XML-declaration sources), the code does NOT throw a `NullPointerException` and falls back to a default encoding (e.g., UTF-8)

4. **Test with a null XMLStreamReader** — the method should handle null input gracefully (e.g., throw `IllegalArgumentException` or return null, depending on contract).

**Common pitfalls to avoid:**
- Testing only that the stream can be read (e.g., calling `readLine()`), without verifying that `close()` propagates to the underlying `XMLStreamReader`
- Forgetting that `XMLStreamReader.getEncoding()` can return `null`, which will cause a `NullPointerException` if passed directly to `Charset.forName()`
- Testing only the happy path with a simple string, without checking edge cases like empty documents, documents with/without XML declaration, or documents with a byte order mark (BOM)

**Concrete example (correct test):**
```java
@Test
public void testBufferedReaderClosesXmlStreamReader() throws Exception {
    String xml = "<?xml version='1.0' encoding='UTF-8'?><root>test</root>";
    XMLInputFactory factory = XMLInputFactory.newInstance();
    XMLStreamReader reader = factory.createXMLStreamReader(new ByteArrayInputStream(xml.getBytes("UTF-8")));
    
    StaxConverter converter = new StaxConverter();
    try (BufferedReader br = converter.toBufferedReader(reader)) {
        assertEquals("<root>test</root>", br.readLine());
    }
    
    // After closing, the reader should throw an exception
    assertThrows(XMLStreamException.class, () -> reader.hasNext());
}
```

**Concrete example (incorrect test — common pitfall):**
```java
// INCORRECT: Doesn't test that close() propagates to the XMLStreamReader
@Test
public void testConversion() throws Exception {
    String xml = "<root>test</root>";
    XMLInputFactory factory = XMLInputFactory.newInstance();
    XMLStreamReader reader = factory.createXMLStreamReader(new ByteArrayInputStream(xml.getBytes("UTF-8")));
    
    StaxConverter converter = new StaxConverter();
    BufferedReader br = converter.toBufferedReader(reader);
    assertEquals("<root>test</root>", br.readLine());
    // Resource leak: br.close() might not close reader, and this test doesn't check
    br.close();
    // No assertion verifying reader was actually closed — test passes but bug exists
}
```