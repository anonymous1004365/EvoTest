---
name: protocol-decoder-incomplete-frame
description: When a protocol frame decoder has an alternative/fallback decoding path
  that may produce incomplete or partially decoded frames without failing, test that
  both the primary and alternative decoding paths produce expected output, especially
  for edge-case payloads that may trigger the fallback path.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-incomplete-frame

## Instructions

# Protocol Decoder Incomplete Frame Handling

## Instructions

- WHEN the TG encounters a protocol decoder class that has an alternative/fallback decoding path (e.g., a secondary `try` block, `if/else` branches for different frame types, or `switch` cases for message subtypes) beyond the primary decoding path
- THEN the TG should write a parametric test that exercises **both** the primary and alternative/fallback decoding paths, by providing different payload variants that activate each path
- The TG should verify that for **all** activated paths, the resulting decoded object has expected non-null fields, expected structure, and no unexpected `null` values for mandatory fields (e.g., device ID, position data, message content)
- When testing the fallback/alternative path, the TG should verify that the decoder doesn't silently produce incomplete objects (e.g., objects whose critical fields are all null) but instead either decodes fully or throws an appropriate exception
- Common pitfalls to avoid:
  - Testing only the "happy path" (primary/prototypical frame format) and missing the alternative decoding path entirely
  - Assuming that because the decoder returns a non-null object, the object is fully decoded — verify specific field values
  - Testing only `String`-type payloads that match the primary format, instead of including payload variations that exercise branching logic

**Example (correct approach):**
```java
@Test
public void testDecodeAlternativePath() {
    EnforaProtocolDecoder decoder = new EnforaProtocolDecoder(new EnforaProtocol());
    
    // Primary path payload
    ByteBuf primaryPayload = Unpooled.wrappedBuffer(ByteUtil.fromHex("..."));
    Object result = decoder.decode(null, null, primaryPayload);
    assertNotNull(result);
    // Verify primary path produces expected object
    
    // Alternative/fallback path payload
    ByteBuf altPayload = Unpooled.wrappedBuffer(ByteUtil.fromHex("..."));
    Object altResult = decoder.decode(null, null, altPayload);
    assertNotNull(altResult);
    // Verify alternative path also produces expected object with non-null fields
}
```

**Example (wrong approach):**
```java
@Test
public void testDecodePrimaryPathOnly() {
    EnforaProtocolDecoder decoder = new EnforaProtocolDecoder(new EnforaProtocol());
    ByteBuf payload = Unpooled.wrappedBuffer(ByteUtil.fromHex("..."));
    Object result = decoder.decode(null, null, payload);
    assertNotNull(result);  // Missing: doesn't test alternative/fallback paths
}
```