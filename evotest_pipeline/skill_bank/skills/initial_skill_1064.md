---
name: alternative-protocol-decoding-path
description: When a protocol frame decoder has an alternative decoding path that fails silently (no frame decoded), tests should verify that the primary path is always used when valid data exists, and that exceptions from the alternative path are properly propagated or the frame is correctly decoded.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING', 'VALIDATION', 'EXCEPTION_HANDLING']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder (e.g., `Gt06ProtocolDecoder`) that implements frame decoding with multiple decoding paths (e.g., a primary path that uses one decoding strategy and an alternative/fallback path for edge cases)
- THEN the TG should write a test that:
  1. Sends valid protocol data that exercises the primary decoding path
  2. Also sends data that explicitly triggers the alternative decoding path (e.g., data with specific length/header values that cause the decoder to take the alternative branch)
  3. Verifies that **both paths produce a correctly decoded frame** (non-null, with expected content)
  4. If the alternative path can fail (e.g., throws an exception or returns null/skipping), verify that on the buggy version the frame is NOT decoded (returns null or skips), while on the fixed version it IS properly decoded
  5. Check for edge cases like: certain byte values causing the decoder to jump to an alternative method; unusual frame lengths that change the decoding strategy; specific header values that route to a different parser
- Common pitfalls to avoid:
  - Testing only the happy path of the decoder (e.g., only sending well-formed standard frames)
  - Assuming the alternative decoding path is never exercised
  - Ignoring empty or edge-case buffers/channel inputs that could trigger fallback logic
  - Not verifying the **content** of the decoded frame (just checking non-null may miss partial decoding issues)
  - Using only high-level integration tests that don't expose the internal branching of the decoder

### Example (Correct — tests both paths, verifies content):

```java
@Test
public void testDecodeWithAlternativePath() throws Exception {
    Gt06ProtocolDecoder decoder = new Gt06ProtocolDecoder(null);
    
    // Primary path: standard frame data
    ByteBuf primaryBuf = Unpooled.copiedBuffer(new byte[]{...standard frame bytes...});
    Object primaryResult = decoder.decode(null, null, primaryBuf);
    assertNotNull("Primary path should decode a frame", primaryResult);
    assertTrue("Primary path should produce a Position", primaryResult instanceof Position);
    
    // Alternative path: data that triggers fallback branch (e.g., unusual length/header)
    ByteBuf altBuf = Unpooled.copiedBuffer(new byte[]{...alt-triggering bytes...});
    Object altResult = decoder.decode(null, null, altBuf);
    assertNotNull("Alternative path should also decode a frame (fixed behavior)", altResult);
    assertTrue("Alternative path should produce a Position", altResult instanceof Position);
    // Verify specific fields are correctly decoded in both paths
    assertEquals(expectedLongitude, ((Position) primaryResult).getLongitude(), 0.001);
    assertEquals(expectedLongitude, ((Position) altResult).getLongitude(), 0.001);
}
```

### Example (Wrong — only tests one path, no content verification):

```java
@Test
public void testDecode() throws Exception {
    Gt06ProtocolDecoder decoder = new Gt06ProtocolDecoder(null);
    ByteBuf buf = Unpooled.copiedBuffer(new byte[]{0x01, 0x02, 0x03});
    // Only sends standard data, never triggers the alternative path
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
    // No check that alternative path also works
    // No content verification that both paths decode fields consistently
}
```