---
name: protocol-decoder-null-attribute-handling
description: Test that protocol decoders handle missing or null optional attributes
  in incoming messages gracefully, especially when those attributes are decoded as
  alternative protocols. Apply when a protocol decoder has multiple branches for parsing
  alternative message formats.
code_tags:
- VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: EXCEPTION_TEST
---

# protocol-decoder-null-attribute-handling

## Instructions

# Protocol Decoder Null Attribute Handling

## Instructions

- WHEN the TG encounters a `ProtocolDecoder` class that decodes messages into positions/attributes with multiple protocol branches (alternative protocols) — for example, where some attributes like `name`, `deviceId`, `protocol`, or custom key-value pairs are parsed from message fields that may be missing or null
- THEN the TG MUST write a test that constructs an incoming message that triggers a code path where an optional attribute (e.g., an identifier string, a numeric field, or a delimited field) is omitted or set to an empty/null value, and verify that `decode()` does NOT throw a `NullPointerException` or `ArrayIndexOutOfBoundsException`
- The test should call `decoder.decode(null, null, message)` with the minimal valid message that exercises the vulnerable attribute access path, and assert that the resulting object (a `Position` or similar) is non-null and has the expected basic fields
- Include concrete values: use the actual raw message format (e.g., a pipe-delimited string like `"|identifier|||value|"`) that causes a null/empty field to be read
- Common pitfalls to avoid:
  - Testing only the "happy path" with all fields present
  - Assuming a field that is present in one message format is present in all alternative formats
  - Catching exceptions in the test's `@Test` annotation without verifying the actual decoded object's state
  - Forgetting that split/parsed arrays may have fewer elements than expected when optional fields are missing

### Example: Correct test

```java
@Test
public void testDecodeWithMissingOptionalAttribute() throws Exception {
    SupermateProtocolDecoder decoder = new SupermateProtocolDecoder(new Protocol("supermate"));
    // Message where the optional name/identifier field (second field) is missing
    String msg = "|123456789012345||100|200|";  // note empty second field
    Position position = decoder.decode(null, null, msg);
    assertNotNull("Position should not be null when optional attribute is missing", position);
}
```

### Example: Incorrect test (insufficient coverage)

```java
@Test
public void testDecodeWithAllFields() throws Exception {
    SupermateProtocolDecoder decoder = new SupermateProtocolDecoder(new Protocol("supermate"));
    String msg = "|123456789012345|deviceName|100|200|";
    Position position = decoder.decode(null, null, msg);
    assertNotNull(position);
    // This only tests the happy path -- missing fields not exercised
}
```