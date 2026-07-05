---
name: alternative-protocol-decoding-path
description: When a protocol decoder has both primary and alternative decoding paths (e.g., based on time buffer or frame checking), the TG should write tests that exercise both branches to ensure the alternative path does not fail with NullPointerException or similar unrecoverable errors.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol frame decoder that uses a `ChannelBuffer` (Netty or similar) and has logic to check whether a received message contains a partial time/date field (e.g., checks `buf.readableBytes()` to decide between normal vs. alternative decoding)
- THEN the TG should write a PARAMETRIC_TEST that sends payloads designed to exercise the alternative decoding branch (e.g., a message shorter than the minimum normal frame, or a message missing the expected trailing time bytes), and assert that the decoder does NOT throw an uncaught `NullPointerException` or `IndexOutOfBoundsException`
- Include a direct test case where a valid prefix is followed by a payload that is too short to contain the alternative time field (e.g., a message of length 4 bytes that should trigger the alternative path), and verify that the decoder produces either `null` (unhandled message) or a decoded position object — but does NOT crash
- Common pitfall: testing only valid, complete frames that always exercise the primary decoding path, thereby missing the bug entirely
- Correct approach example (where a time-buffer-heuristic fails):
```
// Wrong: only tests the primary path with complete 20-byte frames
byte[] buf = { 0x24, 0x24, ... }; // full valid frame

// Correct: also sends a short frame that hits the alternative branch
byte[] buf = { 0x24, 0x24, 0x01, (byte)0x02 }; // only 4 bytes
assertNotNull(decoder.decode(channel, remoteAddr, ChannelBuffers.wrappedBuffer(buf)));
// The fixed decoder should not throw
```
- Include specific failure assertion: if the buggy decoder would throw `NullPointerException` on the alternative path, the test should expect no exception (or expect `null` for an unhandled message)
- Verify that exception handling in the alternative path gracefully returns `null` or continues instead of propagating the error