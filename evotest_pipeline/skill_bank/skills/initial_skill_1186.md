---
name: protocol-handler-missing-buffer-read
description: When a protocol message handler reads from a buffer but the handler is
  invoked multiple times for different message types (alternative decoding paths),
  the buffer position may already be consumed. The TG should test each decoding path
  independently AND also test that each path works when called as a subsequent path
  after the first one has consumed data.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# protocol-handler-missing-buffer-read

## Instructions

# Protocol Handler — Missing Buffer Read After Alternative Decoding Path

## Instructions

- WHEN the TG encounters a protocol decoder that has an `if-else` or `try-catch` structure where one branch decodes a message one way and another branch decodes it differently (alternative decoding paths), AND both branches read from the same `ByteBuf` buffer
- THEN the TG MUST write tests that call both decoding paths sequentially, reusing the same buffer (as if a second message arrives after the first was decoded). This is because the first branch may consume (read) bytes from the buffer, and the second branch may incorrectly assume the buffer is still at its initial position.
- Specifically: after one decoding path reads from the buffer (advancing the reader index), the alternative decoding path must be tested with the buffer in its already-read state to check for `IndexOutOfBoundsException` or incorrect parsing.
- Common pitfalls:
  - Testing each decoding path in isolation with a fresh buffer (this hides the bug because both paths work when buffer position is 0)
  - Assuming that the buffer's reader index resets between alternative decoding paths
  - Only testing with `ByteBuf` at reader index 0
- Example correct test pattern (Java):
  ```java
  // BAD: Tests each path in isolation
  ByteBuf buf1 = Unpooled.copiedBuffer(data1);
  decoder.decode(buf1); // works
  ByteBuf buf2 = Unpooled.copiedBuffer(data2);
  decoder.decode(buf2); // works in isolation

  // GOOD: Tests second path after first path has consumed data
  ByteBuf buf = Unpooled.copiedBuffer(data1, data2); // concatenated
  decoder.decode(buf); // consumes first message, advances reader index
  assertThrows(IndexOutOfBoundsException.class, () -> decoder.decode(buf));
  // OR verify the remaining content is parsed correctly
  ```
- The test should verify that when the alternative decoding path reads from a buffer whose reader index has already been advanced by a previous read, it either throws an appropriate exception or correctly handles the offset.