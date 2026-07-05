---
name: protocol-decoder-alternative-path-length-mismatch
description: WHEN a protocol frame decoder has an alternative decoding path (e.g.,
  based on a serverFlagSplit or similar flag), test with messages that trigger that
  alternative path (e.g., with split=1) to verify the length parsing logic still works
  correctly and does not misinterpret the frame length.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-alternative-path-length-mismatch

## Instructions

# Protocol Decoder Alternative Path Length Mismatch

## Instructions

WHEN a TG encounters a protocol frame decoder that has two decoding paths (e.g., one for `serverFlagSplit == ... != 0` and another for the default case), THEN the TG should write a test that exercises the alternative path with a message that has a different length than expected.

- **Check for flags that branch the decoding logic**: Search for conditions like `if (serverFlagSplit == ...)` or similar boolean/flag checks that change frame length calculation.
- **Test with both `flagSplit = 0` and `flagSplit = 1`**: The default path (split=0) uses a fixed length (e.g., 12 bytes). The alternative path (split=1) should compute length differently (e.g., reading a dynamic length field). Verify that the alternative path computes the correct length.
- **Verify the correct bytes are parsed**: Send a message with a known content (e.g., an alarm message with specific parameters) and assert that the decoded result extracts the correct fields (e.g., alarm type, status, etc.).
- **Expect specific exceptions on the buggy version**: On the buggy version, the alternative path may misinterpret length fields, causing `IndexOutOfBoundsException`, wrong frame boundary detection, or silently wrong protocol field values.

**Common pitfalls to avoid**:
- Testing only the default (non-alternative) decoding path — the bug may only manifest in the alternative branch.
- Not sending messages with varying lengths when testing the alternative path — the length handling discrepancy only appears when the actual payload length differs from the default fixed length.
- Assuming the alternative path works the same as the default path — each path's length computation must be tested independently.

**Example (correct)**:
```java
// Test alternative path with a message that has a different length
// Assuming the default path expects 12 bytes, alternative path should read length dynamically
byte[] alternativeMessage = builder.append(...).append(...)  // With splitFlag=1 and different length
    .build();
ProtocolDecoder decoder = new Gt06ProtocolDecoder(...);
decoder.decode(channel, remoteAddress, alternativeMessage);
// Assert specific decoded fields
```

**Example (incorrect — only tests default path)**:
```java
// Only testing the default path with splitFlag=0 — misses the alternative path bug
byte[] defaultMessage = builder.append(...).append(...)  // Only split=0 scenario
    .build();
ProtocolDecoder decoder = new Gt06ProtocolDecoder(...);
decoder.decode(channel, remoteAddress, defaultMessage);
// Missing the alternative path test entirely
```