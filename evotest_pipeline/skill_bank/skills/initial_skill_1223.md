---
name: tk102-protocol-decoder-null-deviceid
description: ''
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- PROTOCOL_PARSING
- STATE_TRANSITION
test_pattern: EXCEPTION_TEST
---

# tk102-protocol-decoder-null-deviceid

## Instructions

# TK102 Protocol Decoder Null Device ID Handling

## Instructions

- WHEN the TG encounters a protocol decoder that parses device identifier (e.g., IMEI, unique ID) from incoming protocol messages, and the decoding result may return `null` for that identifier
- THEN the TG should write a test that sends a protocol message where the device identifier field is missing, malformed, or resolves to `null`, and verify that:
  1. The decoder does NOT throw a `NullPointerException`
  2. The decoder returns a valid position object or gracefully handles the missing identifier
  3. The test expects either no exception, or a specific checked exception that the decoder is designed to throw
- Common pitfalls:
  - Testing only with well-formed messages that have valid device IDs, missing the case where ID parsing returns null
  - Assuming the decoder always returns a non-null device ID without checking the actual code path for missing/malformed identifiers
  - Not testing the edge case where the device identifier is present in the message but is an empty string or otherwise unparsable

### Correct Example

```java
@Test
public void testDecodeWithMissingDeviceId() {
    Tk102ProtocolDecoder decoder = new Tk102ProtocolDecoder(null);
    // Construct a message where the device identifier field is missing or malformed
    String malformedMsg = "*HQ,123456789012345,V1,012345.000,A,0225.0000,N,...."; // missing/empty ID field
    
    // Expect no NullPointerException — the decoder should handle this gracefully
    assertDoesNotThrow(() -> {
        Object result = decoder.decode(null, null, malformedMsg);
        // Optionally assert on result state
    });
}
```

### Incorrect Example

```java
@Test
public void testDecodeWithMissingDeviceId() {
    Tk102ProtocolDecoder decoder = new Tk102ProtocolDecoder(null);
    String malformedMsg = "*HQ,123456789012345,V1,012345.000,A,0225.0000,N,...";
    
    // WRONG: expects no exception but doesn't verify the decoder can handle null device ID
    // This test would pass even if NPE is thrown because it doesn't catch the exception
    decoder.decode(null, null, malformedMsg); // Missing assertDoesNotThrow!  
}
```

### Key Verification Points

1. The device ID parsing code path — trace what happens when `deviceId` is `null`
2. Any subsequent `.method()` calls on the parsed device ID — these will NPE if the ID is null
3. Whether the decoder's `decode` method uses the parsed device ID before validating it's non-null