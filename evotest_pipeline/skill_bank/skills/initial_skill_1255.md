---
name: gps-protocol-template-hierarchy-validation
description: When decoding GPS protocol messages that produce position data, the decoder
  may produce duplicate positions if it fails to deduplicate against previously decoded
  positions from the same message. This skill teaches how to detect missing deduplication
  logic in protocol decoders.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# gps-protocol-template-hierarchy-validation

## Instructions

# GPS Protocol Message Deduplication Validation

## Instructions

- WHEN the Test Generator encounters a GPS protocol decoder class (e.g., `TeltonikaProtocolDecoder`) that processes a device message into a list of `Position` objects (or one `Position` at a time)
- THEN it should test that multiple records decoded from a single message do not produce duplicate `Position` entries. Specifically:
  - WHEN a single raw message (e.g., a hexadecimal string) decodes into multiple position frames
  - THEN verify that the number of unique decoded positions matches the number of distinct position frames in the message, AND no two positions have identical timestamps, latitudes, longitudes, and other key fields
  - Include a test case where the same device sends two consecutive identical location updates in the same protocol session — the decoder should NOT create duplicate positions
- Common pitfalls:
  - Testing only that the protocol decoder returns at least one position, without checking if it returns MORE positions than expected (duplicates)
  - Using a test message with only a single position frame, which cannot detect deduplication bugs
  - Assuming the framework handles deduplication automatically — protocol decoders must do this themselves
  - Not checking position equality by their semantic fields (timestamp, lat, lon, speed, course), relying only on object identity

### Correct Example (would catch this bug)

```java
// TeltonikaProtocolDecoderTest.java
@Test
public void testDecodeDeduplicatesPositions() throws Exception {
    TeltonikaProtocolDecoder decoder = new TeltonikaProtocolDecoder(new TestProtocol());
    // A message known to produce multiple positions from the same device
    String hexMessage = "...";  // hexadecimal string that triggers multi-position decode
    ByteBuf buf = Unpooled.copiedBuffer(Hex.decodeHex(hexMessage));
    
    Object result = decoder.decode(null, null, buf);
    assertNotNull("Result should not be null", result);
    
    // Result is typically a list of positions or a single position
    List<Position> positions = (result instanceof List) 
        ? (List<Position>) result 
        : Collections.singletonList((Position) result);
    
    // Check for duplicates — group by significant fields
    Set<String> uniqueKeys = new HashSet<>();
    for (Position p : positions) {
        String key = p.getDeviceId() + "|" + p.getFixTime() + "|" 
                   + p.getLatitude() + "|" + p.getLongitude();
        assertTrue("Duplicate position found: " + key, uniqueKeys.add(key));
    }
    
    // Verify we got the expected number of distinct positions
    assertEquals("Expected 2 unique positions from this message", 2, uniqueKeys.size());
}
```

### Incorrect Example (would miss the bug)

```java
// ❌ This test does NOT catch deduplication bugs
@Test
public void testDecode() throws Exception {
    TeltonikaProtocolDecoder decoder = new TeltonikaProtocolDecoder(new TestProtocol());
    String hexMessage = "0000000000000031...";  // single-position message only
    ByteBuf buf = Unpooled.copiedBuffer(Hex.decodeHex(hexMessage));
    
    // Only checks that decoding doesn't crash and returns something
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
    // No validation of position count or deduplication!
}
```