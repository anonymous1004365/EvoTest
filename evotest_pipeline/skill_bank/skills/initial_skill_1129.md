---
name: protocol-character-encoding-length-mismatch
description: When a protocol decoder reads strings by character count (not byte count)
  from a binary buffer, tests must verify that strings with multi-byte characters
  (e.g. Chinese) are correctly decoded and that the reader position advances by the
  correct number of bytes, not the character count.
code_tags:
- VALIDATION
- PROTOCOL_FRAME_DECODER_CHARACTER_ENCODING
test_pattern: PARAMETRIC_TEST
---

# protocol-character-encoding-length-mismatch

## Instructions

# Protocol Character Encoding Length Mismatch Skill

## Instructions

- WHEN the TG encounters a protocol decoder that reads a string from a binary buffer (e.g., `ByteBuf`) using a method like `readString(buf, length)` where `length` is specified as a character count (e.g., number of Unicode characters) rather than a byte count  
- THEN the TG must test with strings containing multi-byte encoded characters (e.g., non-ASCII characters like "éñü" or other characters outside the ASCII range) to verify that:
  1. The string is correctly decoded (the actual string content matches the original)
  2. The reader index (position) in the buffer advances by the correct number of BYTES (not characters), otherwise subsequent fields will be parsed from the wrong offset
- Verify that the buggy version either produces a wrong string or corrupts subsequent fields due to a position mismatch, while the fixed version reads the correct number of bytes
- Common pitfall: testing only with ASCII strings (e.g., "abc123") which have 1:1 byte-to-character ratio — such tests will pass on both buggy and fixed versions and fail to detect the encoding bug
- Include tests with different character lengths (e.g., 1-character Chinese, 3-character Chinese, mixed ASCII+Chinese) to ensure robustness
- ALSO: Check if the decoder reads a "length" or "count" field from the buffer to determine how many characters/bytes to read — this field value itself must match what the decoder expects (byte count vs character count)

### Example (Correct — catches the bug):
```java
// Buggy: readString(buf, charCount) reads charCount bytes instead of calculating real byte length
// Fixed: readString(buf, byteCount) where byteCount = charCount * 3 (or proper charset conversion)

// Test with Chinese characters (3 bytes each in UTF-8)
@Test
public void testDecodeWithChineseCharacters() {
    ByteBuf buf = Unpooled.buffer();
    String nonAscii = "éñü";  // 3 characters, multiple bytes in UTF-8
    byte[] encoded = chinese.getBytes(StandardCharsets.UTF_8);
    buf.writeShort(encoded.length);  // length in bytes = 6
    buf.writeBytes(encoded);
    // ... parse and verify decoded string equals the original non-ASCII string
}
```

### Example (Incorrect — misses the bug):
```java
// Tests only with ASCII — won't detect the encoding bug
@Test
public void testDecodeWithAscii() {
    ByteBuf buf = Unpooled.buffer();
    buf.writeShort(3);  // length = 3
    buf.writeBytes("abc".getBytes(StandardCharsets.UTF_8));  // 3 bytes = 3 chars, works by accident
    // ... parse and verify "abc" — passes on both buggy and fixed!
}
```