---
name: eelink-protocol-type-id-array-decode
description: When decoding Eelink protocol messages, the decoder uses a type-ID dispatch
  to handle different message types. Unknown message types or edge cases in type dispatching
  may cause the decoder to misinterpret data or fail entirely. This skill teaches
  how to write tests that verify correct type identification and data extraction for
  each protocol message type.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- NULL_CHECK
- VALIDATION
- PROTOCOL_MESSAGE_TYPE_SWITCH
test_pattern: PARAMETRIC_TEST
---

# eelink-protocol-type-id-array-decode

## Instructions

# Eelink Protocol Type-ID Array Decode

## Instructions

### WHEN the TG encounters:
- A protocol decoder (`EelinkProtocolDecoder`) that reads a type ID from a buffer (e.g., `buf.readUnsignedByte()`) and dispatches to different decoding logic using a `switch` statement or if-else chain
- The decoder processes different message types such as `MSG_LOGIN`, `MSG_HEARTBEAT`, `MSG_GPS`, `MSG_STATUS`, etc.
- The decoder uses `ChannelBuffer` or similar binary buffer reading methods (e.g., `buf.readUnsignedByte()`, `buf.readUnsignedShort()`, `buf.readBytes()`)

### THEN the TG should:

1. **Test each protocol message type separately** with minimal valid payloads. For each type ID value (e.g., `0x01` for MSG_LOGIN, `0x02` for MSG_HEARTBEAT, `0x12` for MSG_GPS), create a test method or a parameterized test case that:
   - Constructs a binary payload with the correct type ID at the expected position
   - Fills in the expected fields for that message type with known values
   - Calls the decoder and asserts the resulting position object has the correct decoded values

2. **Test with an unknown/reserved type ID** (e.g., `0xFF`) to verify the decoder handles it gracefully without throwing an exception or producing a corrupt result.

3. **Test edge cases for numeric fields** that the decoder extracts:
   - When the decoder reads `buf.readUnsignedByte()` values (e.g., course, speed, status), test with boundary values like `0`, `1`, `255`, `254`
   - When the decoder reads `buf.readUnsignedShort()` values (e.g., battery level, temperature), test with `0`, `65535`, and mid-range values
   - When the decoder reads coordinate values, test with positive and negative values that span the range of `double`

4. **Test with minimal/truncated payloads** to ensure the decoder validates buffer readability before reading, and throws an appropriate exception (e.g., `IndexOutOfBoundsException` or a custom decode error) rather than silently returning a partial result.

5. **Test that position attributes are correctly populated** — for example, if MSG_GPS decoding sets attributes like `"battery"`, `"temperature"`, `"status"`, verify those attributes are present and have correct values in the decoded `Position` object.

### Common pitfalls to avoid:
- Testing only the first/primary message type (e.g., only MSG_LOGIN) and assuming other types work similarly — always test ALL relevant message types
- Testing with only "happy path" data where all fields are zero or default — exercise realistic non-zero values
- Forgetting to test unknown/reserved type IDs — the decoder should either handle them gracefully or explicitly fail
- Assuming `ChannelBuffer` read methods won't throw — always test with buffer sizes that are too small
- Checking the wrong position fields — reference the protocol specification to know which Position fields each message type populates

### Example (correct approach):

```java
// Example: Parameterized test for Eelink protocol decoder
@ParameterizedTest
@CsvSource({
    "1, 1, 55.5, 37.6, 10.0, 90",          // MSG_GPS with typical values
    "1, 0, 0.0, 0.0, 0.0, 0",               // MSG_GPS with zeros (edge case)
    "1, 255, -90.0, -180.0, 255.0, 255",    // MSG_GPS with boundary values
    "3, 100, , , , "                         // MSG_STATUS with only type and status
})
void testDecodeMessageType(int msgType, int status, Double latitude, Double longitude, Double speed, Integer course) {
    EelinkProtocolDecoder decoder = new EelinkProtocolDecoder(null);
    ChannelBuffer buf = ChannelBuffers.buffer(64);
    // Build header: type, status, then type-specific fields
    buf.writeByte(0x12); // MSG_GPS
    buf.writeByte(status);
    if (msgType == 1) { // MSG_GPS
        // Write latitude, longitude, speed, course, etc.
        // ... write expected binary format
    } else if (msgType == 3) { // MSG_STATUS
        // Write status-specific payload
    }
    Position position = decoder.decode(null, null, buf);
    assertNotNull(position);
    // Verify decoded fields match expected values
}
```

### Example (incorrect approach to avoid):

```java
// BAD: Only tests one message type with zero values
@Test
void testDecode() {
    EelinkProtocolDecoder decoder = new EelinkProtocolDecoder(null);
    ChannelBuffer buf = ChannelBuffers.buffer(16);
    buf.writeByte(0x01); // only MSG_LOGIN
    buf.writeByte(0);
    buf.writeByte(0);
    buf.writeByte(0);
    // ... only zeros
    Position position = decoder.decode(null, null, buf);
    assertNotNull(position);
    // Does not verify any actual field values!
}
```