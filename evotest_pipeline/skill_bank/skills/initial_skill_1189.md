---
name: protocol-alternative-decoder-path-validation
description: When a protocol decoder has an alternative decoding path (e.g., with
  supplementary data or fallback parsing), test all code paths including error handling.
  Tests should verify that malformed or partially valid inputs in alternative paths
  produce clear exceptions or null results instead of silent failures.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# protocol-alternative-decoder-path-validation

## Instructions

# Protocol Alternative Decoder Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `JpKorjarProtocolDecoder`) that contains multiple or alternative decoding paths — such as handling supplementary data, fallback formats, or optional message fields — and one of those alternative paths does not properly validate its inputs or handle missing data
- THEN the TG should write a test that:
  1. Constructs a valid base message plus **invalid** or **missing** data for the alternative path (e.g., missing supplementary position data, truncated fields, or malformed optional segments)
  2. Calls the decoder's decode or channel read method with this input
  3. Verifies that the decoder either:
     - Throws an explicit exception (e.g., `IllegalArgumentException`, `IndexOutOfBoundsException`, `RuntimeException`) with a meaningful message
     - Returns a `null` result (indicating the message could not be parsed)
     - Logs a clear error rather than silently returning an incorrect/partial result
  4. Includes negative cases where only the alternative path is triggered with invalid data, not just the primary parsing path

- Common pitfalls to avoid:
  - Testing only the "happy path" primary decoding and omitting alternative branching logic
  - Assuming that because a message header parses successfully, all sub-fields are guaranteed to exist
  - Writing tests that expect a successful decode result when the alternative path would produce an incomplete or wrong result
  - Forgetting to test with inputs that hit edge conditions in the alternative path (e.g., empty supplementary data, missing optional fields, truncated arrays)

- Example correct test pattern:
```java
@Test
public void testDecodeWithMalformedSupplementaryData() throws Exception {
    // Build a message with a valid header but invalid supplementary position data
    // that triggers the alternative decoding path
    ByteBuf buf = Unpooled.buffer();
    buf.writeBytes(HexUtil.decodeHex("...valid header..."));
    buf.writeBytes(HexUtil.decodeHex("...truncated data..."));
    
    Object result = decoder.decode(null, null, buf);
    
    // Either the decoder should return null (skip invalid message)
    // OR throw an exception clearly indicating the failure
    assertNull("Decoder should return null for invalid alternative path data", result);
    // OR expect exception:
    // assertThrows(IllegalArgumentException.class, () -> decoder.decode(null, null, buf));
}
```

- Example incorrect test pattern (what to avoid):
```java
@Test
public void testDecodeOnlyHappyPath() throws Exception {
    // Only tests the primary decoding path, never exercises the alternative path
    ByteBuf buf = Unpooled.buffer();
    buf.writeBytes(HexUtil.decodeHex("...fully valid message..."));
    
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
    // This passes but misses that the alternative path is broken
}
```