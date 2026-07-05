---
name: protocol-decoder-numeric-field-parsing
description: When a protocol decoder parses numeric fields (like temperature, battery)
  from string attributes that may be null or have blank/empty values, the TG should
  test fields with null, empty string, and non-numeric string inputs to verify the
  decoder handles missing attributes gracefully without throwing unexpected exceptions.
code_tags:
- VALIDATION
- NULL_CHECK
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-numeric-field-parsing

## Instructions

# Protocol Decoder Numeric Field Parsing

## Instructions

- WHEN the TG encounters a protocol decoder that parses numeric fields (e.g., temperature, battery level, speed) from string attribute values obtained from a device message (e.g., using `String` values from a map of string key-value pairs, parsing them with `Double.parseDouble()` or `Integer.parseInt()` or `Double.valueOf()`)
- THEN the TG should test that each numeric field handles missing or malformed attributes correctly. Specifically:
  - Test with a message where the attribute key is **missing entirely** from the input (e.g., the map does not contain the key at all)
  - Test with a message where the attribute value is an **empty string** `""`)
  - Test with a message where the attribute value is a **non-numeric string** (e.g., `"invalid"`)
  - For each case, verify that the decoder does **not** throw a `NullPointerException` or `NumberFormatException`, but instead either skips the field gracefully (no position attribute set for that field) or logs/handles the error without crashing the entire decode
- Common pitfalls to avoid:
  - Testing only a well-formed full message that parses all fields correctly (this masks missing-field handling bugs)
  - Assuming that a missing key in the input map returns an empty string `""` — it returns `null`, which may cause `NullPointerException` on `.isEmpty()` or `.equals()`
  - Only checking for one type of bad input (e.g., only null, but not empty string or non-numeric string)
  - Writing a test that catches all exceptions silently — instead, the test should verify that the decoder produces a valid result (e.g., `Position` object) without the numeric field set, or without throwing

**Correct example:**
```java
// Test with empty string value
@Test
public void testDecodeWithEmptyTemperature() throws Exception {
    CradlepointProtocolDecoder decoder = new CradlepointProtocolDecoder(null);
    // ... create device message where "temperature" attribute is ""
    Position position = decoder.decode(channel, remoteAddress, msg);
    assertNotNull(position);
    // verify temperature was NOT set (or set to 0.0 / default)
    assertNull(position.getAttributes().get(Position.KEY_TEMPERATURE));
}

// Test with missing temperature key
@Test
public void testDecodeWithMissingTemperature() throws Exception {
    CradlepointProtocolDecoder decoder = new CradlepointProtocolDecoder(null);
    // ... create device message WITHOUT a "temperature" attribute
    Position position = decoder.decode(channel, remoteAddress, msg);
    assertNotNull(position);
    assertNull(position.getAttributes().get(Position.KEY_TEMPERATURE));
}
```

**Incorrect example:**
```java
// Only tests the happy path — misses the null/empty bug entirely
@Test
public void testDecode() throws Exception {
    CradlepointProtocolDecoder decoder = new CradlepointProtocolDecoder(null);
    Position position = decoder.decode(channel, remoteAddress, msgWithAllFields);
    assertNotNull(position);
    assertEquals(25.5, position.getAttributes().get(Position.KEY_TEMPERATURE));
}
```