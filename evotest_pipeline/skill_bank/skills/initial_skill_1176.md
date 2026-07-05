---
name: protocol-frame-decoder-alternative-path
description: When a protocol decoder has alternative decoding paths (e.g. different ChannelBuffer read methods), test all paths to ensure consistent frame construction. This skill catches bugs where one code path produces wrong results due to missing state mutation or incorrect type handling.
code_tags: ['VALIDATION', 'TYPE_CONVERSION', 'STATE_MUTATION']
test_pattern: STATE_TEST
---

# protocol-frame-decoder-alternative-path

## Instructions

# Protocol Frame Decoder Alternative Path Testing

## Instructions

- WHEN the TG encounters a protocol message decoder with a frame decoder that has an `OR`-based condition (using `||`) choosing between different reading strategies (e.g., `readUnsignedShort()`, `readInt()`, `readableBytes()`, `toString()`), and different branches return different types of `ChannelBuffer` objects
- THEN the TG MUST write a test that exercises **each alternative branch** of the frame decoder separately, providing input that triggers each condition side, and verify that the decoded frame content is correct and consistent across all branches
- Include test cases where:
  1. The first branch of the OR condition is satisfied (e.g., message length fits in one data type) — verify the frame is correctly assembled with proper content and length
  2. The second branch of the OR condition is satisfied (e.g., message length requires a different data type) — verify the frame is correctly assembled with proper content and length
  3. Edge cases at the boundary between branches (e.g., the smallest/largest value that still triggers each branch)
- The test MUST compare the decoded result (positions, length, content) against expected values, not just check that no exception is thrown
- **Common pitfalls to avoid:**
  - Testing only one branch of the conditional logic (the most common path), leaving the alternative path untested
  - Only testing that decoding succeeds without verifying the correctness of the decoded output (e.g., checking buffer position, content, or length)
  - Not providing input data that exercises the exact boundary conditions between branches
  - Assuming that the frame decoder correctly mutates state (e.g., buffer reader index position) the same way in all branches

### Incorrect example (tests only one path):
```java
ChannelBuffer buf = ChannelBuffers.buffer(10);
buf.writeShort(5); // only triggers first branch
buf.writeBytes("Hello".getBytes());
DmtProtocolDecoder decoder = new DmtProtocolDecoder(null);
ChannelBuffer result = decoder.decode(null, null, buf);
assertNotNull(result);
```

### Correct example (tests all paths with state verification):
```java
// Test first branch (readUnsignedShort path)
ChannelBuffer buf1 = ChannelBuffers.buffer(10);
buf1.writeShort(5); // message length fits in short
buf1.writeBytes("Hello".getBytes());
buf1.writerIndex(7);
ChannelBuffer result1 = decoder.decode(null, null, buf1);
assertEquals(7, result1.writerIndex()); // verify correct position

// Test second branch (readInt path)  
ChannelBuffer buf2 = ChannelBuffers.buffer(10);
buf2.writeInt(5); // alternative reading
buf2.writeBytes("World".getBytes());
buf2.writerIndex(9);
ChannelBuffer result2 = decoder.decode(null, null, buf2);
assertEquals(9, result2.writerIndex()); // verify correct position
```