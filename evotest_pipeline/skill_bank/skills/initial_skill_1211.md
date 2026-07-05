---
name: alternative-protocol-decoding-status-validation
description: When a protocol decoder has multiple decoding paths (e.g., main vs. alternative),
  tests should cover the alternative path by sending data that bypasses the main path.
  This skill teaches how to construct inputs that exercise alternative decoding branches
  in protocol decoders.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: INTERACTION_TEST
---

# alternative-protocol-decoding-status-validation

## Instructions

# Alternative Protocol Decoding Path Testing

## Instructions

- WHEN the TG encounters a protocol decoder that has an alternative decoding path (detected by looking for conditions that redirect to an alternative parsing method, e.g., `alt`/`else` branches that call different decode logic)
- THEN the TG should construct test inputs that:
  1. **Fail the primary path condition** so the alternative path is exercised. This means sending protocol data that does NOT match the main pattern (e.g., missing a prefix, wrong length, or invalid header) but still matches the expected alternative format.
  2. **Include realistic alternative payload fields** such as status bits, sensor values, coordinates (latitude/longitude), speed, course, and other device-specific fields that the alternative path expects to parse.
  3. **Convert the payload correctly to the format expected by the decoder** (e.g., hex string to a byte array buffer wrapped in a ChannelBuffer).
  4. **Verify the decoded object contains the expected device protocol data** — assert that specific fields like status, speed, course, power, and coordinates are correctly populated according to the alternative parsing logic.
  - Include concrete values: provide exact hex strings, deviated coordinates (with offsets), and expected numeric values for all fields the alternative path decodes.
  - Common pitfalls: testing only the main/primary path; constructing hex strings that the main path catches first; not verifying decoded field values against the alternative path's expected format; forgetting that the main path may throw an exception for invalid data and the alternative path catches it.

### Correct Example (actual fix):
```java
// WHEN the main path requires a specific prefix/pattern but alternative path handles other formats:
// THEN construct a hex payload that will NOT match the main path, but matches alternative path

// Primary path expects status messages matching specific patterns (e.g., length checks, prefix bytes)
// Alternative path is a catch-all for other message types

String hexData = "0D0103...";  // Construct hex that skips the main path
byte[] bytes = ByteBufUtil.decodeHexBytes(hexData);
ChannelBuffer buf = ChannelBuffers.wrappedBuffer(bytes);

ProtocolDecoder decoder = new H02ProtocolDecoder(null);
Object decoded = decoder.decode(null, null, buf);
// Assert the decoded object is a Position with expected values
assertNotNull("Should decode on alternative path", decoded);
assertTrue(decoded instanceof Position);
// Verify alternative path field parsing (e.g., status bits, lat/lon with offsets, speed, course)
```

### Incorrect Example (common pitfall):
```java
// BAD: Only testing the main decoding path
String hexData = "MP" + ...; // Only matches main path prefix
// Missing: test with alternative path format
// Missing: test that triggers the else/catch branch in the decoder
```

### Common Pitfalls:
1. **Testing only the primary path** — always check for at least two test inputs that cover both main and alternative branches.
2. **Using hex data that the main path intercepts** — the main path may throw an exception causing the alternative path to never be reached because it catches subclass exceptions outside the decoder's try/catch logic.
3. **Not verifying decoded field values** — asserting only that decoding succeeds is insufficient; the alternative path may decode fields differently (e.g., coordinate offsets, different status bit positions).
4. **Ignoring the exception handling** — the alternative path may be inside a catch block for exceptions thrown by the main path; ensure the test input triggers the main path to throw the correct exception type.