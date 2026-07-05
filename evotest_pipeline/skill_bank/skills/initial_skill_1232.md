---
name: alternative-protocol-decoding-path-validation
description: When a protocol decoder has multiple alternative decoding paths based
  on frame data patterns, tests must verify that at least one path succeeds and that
  corner-case data patterns don't cause all paths to silently fail. This skill teaches
  how to construct test inputs that exercise each alternative decoding branch.
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path-validation

## Instructions

# Alternative Protocol Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder that uses conditional logic (e.g., if-else branches or try-catch blocks) to choose between multiple alternative decoding paths based on the content of incoming frame data
- THEN it should write parameterized tests that feed each alternative path with specially crafted data patterns that exercise each branch, and verify that the decoder produces a valid, non-null decoded result for each meaningful alternative
- Include concrete test data for each branch: e.g., if the decoder distinguishes between "type A" and "type B" messages based on a prefix byte or length field, provide one test input with each prefix/length value
- The test should assert that the result is non-null and that the position/index of the buffer has advanced past the consumed frame; for the buggy version, if a path silently skips decoding (e.g., returns null without consuming), the test should catch this by verifying the position did not advance
- Common pitfalls to avoid:
  - Testing only the "happy path" that worked before the bug — always test at least two alternatives
  - Forgetting to verify that the buffer position/index advances after a successful decode
  - Treating a null returned result as a valid "skip" — consider that null without position advancement may indicate a buggy path
  - Not testing with the exact byte sequences that match each branch condition

### Example (Correct — Catches the Bug):

```java
// Given a decoder that on frame with prefix byte 0x01 uses path A, 
// and on prefix byte 0x02 uses path B, test both:
@Test
public void testAlternativeDecodingPaths() {
    TzoneProtocolDecoder decoder = new TzoneProtocolDecoder(null);
    
    // Path A (prefix 0x01)
    ByteBuf bufA = Unpooled.copiedBuffer(new byte[]{0x01, 0x02, 0x03, 0x04});
    Object resultA = decoder.decode(null, null, bufA);
    assertNotNull("Path A should produce a result", resultA);
    
    // Path B (prefix 0x02)  
    ByteBuf bufB = Unpooled.copiedBuffer(new byte[]{0x02, 0x05, 0x06, 0x07});
    Object resultB = decoder.decode(null, null, bufB);
    assertNotNull("Path B should produce a result", resultB);
}
```

### Example (Incorrect — Misses the Bug):

```java
// Only testing one path — may miss a bug in the alternative branch
@Test
public void testDecode() {
    TzoneProtocolDecoder decoder = new TzoneProtocolDecoder(null);
    ByteBuf buf = Unpooled.copiedBuffer(new byte[]{0x01, 0x02, 0x03, 0x04});
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
    // Never tested what happens with prefix 0x02!
}
```