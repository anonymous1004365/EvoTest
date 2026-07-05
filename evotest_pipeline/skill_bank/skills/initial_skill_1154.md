---
name: decoder-protocol-alternative-path-validation
description: WHEN the TG encounters a protocol decoder with alternative parsing paths
  (e.g., try-catch or fallback logic) for device messages, THEN it should test each
  alternative path individually with protocol data that triggers that specific branch.
  This skill applies to protocol decoders that parse position/location data and have
  multiple code paths for different message formats.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# decoder-protocol-alternative-path-validation

## Instructions

# Protocol Decoder Alternative Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., a class extending `BaseProtocolDecoder` or similar) that has a `try-catch` block wrapping message parsing logic, with a fallback or alternative parsing path in the `catch` block
- THEN the TG should write parametric tests that exercise **each** alternative parsing path separately, using protocol data crafted to trigger that specific branch
- Specifically:
  1. Identify the primary parsing logic and the alternative/fallback parsing logic
  2. For the primary path: provide valid protocol data that passes through the `try` block
  3. For the alternative path: provide protocol data that triggers the `catch` block (e.g., malformed data that causes a parsing exception in the primary path but can still be parsed by the fallback)
  4. Verify that **both** paths produce a correct result (e.g., a valid position object with expected latitude/longitude values)
- Common pitfalls to avoid:
  - **Only testing the primary path**: The fallback path may have bugs (e.g., incorrect field offsets, wrong byte order, sign errors) that remain hidden if not tested
  - **Assuming all protocol data parsing uses the same type logic**: Different parsing branches may handle type conversions differently (e.g., one path may use `Integer.parseInt()` while another uses custom byte manipulation)
  - **Not testing with realistic malformed data**: The fallback path might be triggered by specific real-world protocol variations, not just random garbage

### Correct Example

```java
// Test primary parsing path
@Test
public void testDecodePrimaryPath() throws Exception {
    AutoFonProtocolDecoder decoder = new AutoFonProtocolDecoder(null);
    // Provide valid protocol data that goes through the try block
    String data = "..."; // primary format
    Position position = decoder.decode(data);
    assertNotNull(position);
    assertEquals(expectedLat, position.getLatitude(), 0.001);
}

// Test alternative parsing path
@Test
public void testDecodeAlternativePath() throws Exception {
    AutoFonProtocolDecoder decoder = new AutoFonProtocolDecoder(null);
    // Provide data that triggers the catch/alternative block
    String data = "..."; // alternative format that throws in primary path
    Position position = decoder.decode(data);
    assertNotNull(position);
    assertEquals(expectedLat, position.getLatitude(), 0.001); // verify correct value
}
```

### Incorrect Example (common mistake)

```java
// BUGGY: Only tests the primary parsing path
@Test
public void testDecode() throws Exception {
    AutoFonProtocolDecoder decoder = new AutoFonProtocolDecoder(null);
    String data = "..."; // only primary format
    Position position = decoder.decode(data);
    assertNotNull(position);
    // Never tested the fallback path!
}
```