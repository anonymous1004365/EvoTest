---
name: bom-input-stream-encoding-handling
description: When wrapping an InputStream with BOMInputStream inside XmlReader, the
  BOMInputStream may fail to correctly report encoding after consuming BOM bytes.
  Test that XmlReader correctly returns UTF-8 encoding when input contains a UTF-8
  BOM (byte order mark) followed by an XML declaration with encoding.
code_tags:
- RESOURCE_MANAGEMENT
- VALIDATION
- ENCODING_ESCAPING
test_pattern: STATE_TEST
---

# bom-input-stream-encoding-handling

## Instructions

# BOM InputStream Encoding Handling

## Instructions

WHEN the TG encounters code that wraps an `InputStream` with `BOMInputStream` (e.g., `new BOMInputStream(inputStream)`) inside an `XmlReader` or similar encoding-detection reader class, and then uses `inputStream.mark()` / `inputStream.reset()` to read the XML declaration:

- THEN the TG should create a test that provides an input stream whose first three bytes are the UTF-8 BOM (`0xEF, 0xBB, 0xBF`) followed by an XML declaration like `<?xml version="1.0" encoding="UTF-8"?>` and then content such as `<html></html>`.
- THEN the test should verify that `reader.getEncoding()` returns `"UTF-8"` and not `null`.
- THEN the test should verify that the content can be read correctly (e.g., `<html>` is present after skipping the BOM and XML declaration).
- THEN use a `ByteArrayInputStream` with the raw bytes to construct the input stream, ensuring the BOM bytes are physically present at the start.

Common pitfalls:
- Testing only the BOM without an XML declaration, or testing only the XML declaration without a BOM — but not both together. The bug is that the BOM + XML declaration combination causes the encoding to be lost.
- Assuming the BOM is a character (like `\uFEFF`) rather than raw bytes (`0xEF, 0xBB, 0xBF`). The BOM must be provided as raw bytes in the `byte[]`, not as a Java `String` character.
- Testing the `BOMInputStream` in isolation rather than through the `XmlReader` which is where the bug manifests (the interaction between `BOMInputStream` consuming bytes and `XmlReader` doing `mark`/`reset`).

### Example: Correct test pattern

```java
@Test
public void readHtmlFileWithBomAndXmlPreambleWithEncoding() throws Exception {
    // BOM bytes (UTF-8) followed by <?xml version="1.0" encoding="UTF-8"?><html></html>
    byte[] data = new byte[] {
        (byte)0xEF, (byte)0xBB, (byte)0xBF,  // UTF-8 BOM
        '<', '?', 'x', 'm', 'l', ' ', 'v', 'e', 'r', 's', 'i', 'o', 'n', '=',
        '"', '1', '.', '0', '"', ' ', 'e', 'n', 'c', 'o', 'd', 'i', 'n', 'g', '=',
        '"', 'U', 'T', 'F', '-', '8', '"', '?', '>',
        '<', 'h', 't', 'm', 'l', '>', '<', '/', 'h', 't', 'm', 'l', '>'
    };
    XmlReader reader = new XmlReader(new ByteArrayInputStream(data), null);
    assertEquals("UTF-8", reader.getEncoding());
    // Read content to verify reader works
    char[] buf = new char[100];
    int len = reader.read(buf, 0, buf.length);
    String content = new String(buf, 0, len);
    assertTrue(content.contains("<html>"));
}
```

### Example: Incorrect test pattern (would miss the bug)

```java
@Test
public void readHtmlFileWithBomOnly() throws Exception {
    // Only has BOM, no XML declaration — won't trigger the bug
    byte[] data = new byte[] {
        (byte)0xEF, (byte)0xBB, (byte)0xBF,
        '<', 'h', 't', 'm', 'l', '>'
    };
    XmlReader reader = new XmlReader(new ByteArrayInputStream(data), null);
    // This would pass even on the buggy version because encoding comes from default
    assertNull(reader.getEncoding()); // Still works but doesn't test the bug
}
```