---
name: protocol-tlv-trailer-length-validation
description: When decoding TLV (Type-Length-Value) protocol messages, validate that
  the length field of each TLV entry does not exceed the remaining buffer bytes. For
  Teltonika protocol decoding, verify the decoder throws an appropriate exception
  or handles truncated trailers gracefully.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- ARRAY_INDEX_ACCESS
- BOUNDARY_CHECK
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# protocol-tlv-trailer-length-validation

## Instructions

# Protocol TLV Trailer Length Validation

## Instructions

- WHEN the TG encounters a protocol decoder that parses TLV (Type-Length-Value) entries from a byte buffer, especially fields tagged as "trailer" or "event" data following the main GPS payload
- THEN the TG must write a test that sends a malformed buffer where a TLV length field specifies a value greater than the number of remaining bytes in the buffer (i.e., a truncated trailer)
  - Verify that the decoder throws an appropriate exception (e.g., `RuntimeException`, `IllegalArgumentException`, or a buffer underflow exception) or handles the truncated data gracefully without silent data corruption
  - Test with concrete values: e.g., a buffer whose trailer length field claims 100 bytes but only 5 bytes remain
  - Test with boundary cases: length = 0 (valid empty trailer), length = remaining bytes (valid full trailer), length = remaining bytes + 1 (truncated/invalid)
  - Include test cases where the buffer ends immediately after the length field (completely missing value bytes)
- Common pitfalls to avoid:
  - Testing only with valid/well-formed protocol buffers — malformed/truncated data must also be tested
  - Assuming the decoder throws `ArrayIndexOutOfBoundsException` — the fix may involve catching this and throwing a more specific exception
  - Not testing null/empty buffers for the trailer section specifically

### Correct Example (Java/JUnit):
```java
@Test(expected = RuntimeException.class)
public void testDecodeTruncatedTrailer() throws Exception {
    // Buffer with valid IMEI/GPS data but trailer TLV length says 10 bytes when only 2 remain
    byte[] truncatedTrailer = {
        0x00, 0x0F, 0x32, 0x38, 0x36, 0x31, 0x38, 0x31, 0x30, 0x33,
        0x38, 0x31, 0x32, 0x33, 0x34, 0x35, 0x00, 0x04, // codec 8, 4 records
        // ... valid GPS data ...
        0x00, 0x01, 0x01, 0x0A, 0x05 // type=0x01, length=10, only 2 bytes of value remain
    };
    TeltonikaProtocolDecoder decoder = new TeltonikaProtocolDecoder(null);
    decoder.decode(null, null, Unpooled.wrappedBuffer(truncatedTrailer));
}
```

### Incorrect Example (too narrow — tests only valid case):
```java
@Test
public void testDecodeValidTrailer() throws Exception {
    byte[] validMsg = { /* complete, well-formed message */ };
    TeltonikaProtocolDecoder decoder = new TeltonikaProtocolDecoder(null);
    Object result = decoder.decode(null, null, Unpooled.wrappedBuffer(validMsg));
    assertNotNull(result);
    // Does NOT test truncated trailer — bug remains uncaught
}
```