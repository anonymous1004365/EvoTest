---
name: alternative-protocol-decoding-fallback
description: WHEN decoding network protocol messages where there is an alternative/fallback decoding path (e.g., try-catch with a different buffer parser), THEN the TG should test both the primary and the fallback decoding paths to ensure the fallback path does not corrupt the decoded result. The bug occurs when the primary path fails (e.g., throws an exception) and the fallback path processes additional bytes from the buffer, leading to incorrect field extraction.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-fallback

## Instructions

# Alternative Protocol Decoding Fallback

## Instructions

- WHEN the TG encounters a protocol decoder that has a try-catch block where a primary decoding attempt is wrapped in try and a fallback/alternative decoding path is executed in the catch block
- THEN the TG should create a test that sends a protocol buffer that is structured to intentionally trigger the primary path to throw an exception (e.g., by using a buffer with additional unexpected bytes or a malformed field that the primary path tries to parse), so that the fallback path executes
- The test MUST verify that the fallback path correctly decodes the message by checking the decoded position fields, device identifiers, and any other decoded attributes — not just that no exception is thrown
- Specifically, verify that:
  1. The protocol decoder returns a non-null result
  2. The decoded position has the correct latitude/longitude or coordinates (depending on the protocol)
  3. The decoded position has a valid device ID or unique ID extracted from the buffer
  4. No fields are incorrectly merged or corrupted (e.g., time fields, status fields)
- Common pitfalls to avoid:
  - ❌ Testing only a well-formed buffer that follows the primary path — this does not exercise the fallback
  - ❌ Testing only that the fallback does not throw — the bug may silently produce wrong values
  - ❌ Assuming the fallback path handles the same number of bytes as the primary path
  - ❌ Not checking the decoded position fields (time, coordinates, device ID)
  - ✅ Correct: Create a buffer where the primary path reads an unexpected byte that causes an array index issue, forcing the catch block to execute the alternative decoder, then assert all fields of the decoded position

- **Example of a correct test (pseudocode)**:
```java
// Buffer design: first byte (packet length) is 28, but actual data has only 24 bytes.
// The primary decoder reads more bytes than available, throws an exception, and the fallback kicks in.
byte[] buf = {
  28,           // packet length (triggers primary to read more bytes than available)
  2,            // protocol version
  (byte)0x0C, (byte)0x1E, (byte)0x47, (byte)0x5A, // device ID bytes
  // ... time bytes, coordinate bytes in fallback format
};
Buffer buffer = ChannelBuffers.wrappedBuffer(buf);
CellocatorProtocolDecoder decoder = new CellocatorProtocolDecoder(...);
Position position = (Position) decoder.decode(null, null, buffer);

assertNotNull(position);
assertEquals("expectedDeviceId", position.getDeviceId());
assertEquals(expectedLatitude, position.getLatitude(), 0.001);
assertEquals(expectedLongitude, position.getLongitude(), 0.001);
// Verify time and other fields
```

- **Example of an incorrect test (pseudocode)**:
```java
// ❌ Only tests the happy path (primary decoder) — fallback never executes
byte[] buf = { /* well-formed, small buffer that primary path handles normally */ };
Buffer buffer = ChannelBuffers.wrappedBuffer(buf);
CellocatorProtocolDecoder decoder = new CellocatorProtocolDecoder(...);
Position position = (Position) decoder.decode(null, null, buffer);
assertNotNull(position);
// ❌ Does not check the decoded field values — only checks non-null
// ❌ The buggy fallback could produce wrong coordinates and this test would still pass
```