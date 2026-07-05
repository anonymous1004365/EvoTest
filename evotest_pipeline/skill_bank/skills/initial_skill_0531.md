---
name: gt06-protocol-position-validation
description: When decoding GPS protocol data with multiple position fields (like LBS
  and GPS), test that a valid GPS position is correctly preferred over or merged with
  other position data, and that null/invalid fields do not corrupt the final position.
  Apply this skill when protocol decoders have branching logic for position data from
  multiple sources.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# gt06-protocol-position-validation

## Instructions

# Gt06 Protocol: Position Field Override and Null Safety

## Instructions

- WHEN the TG encounters a protocol decoder (e.g., from the `Gt06ProtocolDecoder` family) that processes multiple types of position-related data (e.g., LBS (cell tower) position data and GPS position data) within the same decoding step
- THEN the TG MUST write tests that:
  1. **Provide both GPS and LBS position data simultaneously** in the same decoded message, and verify that the final `Position` object contains the correct merged/preferred values (e.g., GPS coordinates should take precedence, but LBS fields like `mcc`, `mnc`, `lac`, `cellId` should still be populated from the LBS data).
  2. **Provide LBS data without GPS data** and verify that the decoder still produces a valid `Position` with LBS-derived coordinates and all LBS fields (`mcc`, `mnc`, `lac`, `cellId`) set correctly.
  3. **Provide GPS data without LBS data** and verify that the decoder produces a valid `Position` with GPS coordinates and LBS fields are either absent or set to reasonable default values (e.g., 0 or null).
  4. **Provide partial/protocol-malformed position data** (e.g., missing fields, zero coordinates) and verify the decoder does not throw an unexpected exception or produce a garbled `Position` object.
  5. Verify that **accessing fields on the `Position` returned by the decoder** (e.g., `position.getLatitude()`, `position.getLongitude()`, `position.getAttributes().get(Position.KEY_MCC)`, etc.) does not throw a `NullPointerException` or produce inconsistent results.

- Common pitfalls to avoid:
  - **Testing only one data source**: Testing only GPS data or only LBS data without testing their interaction/merge.
  - **Forgetting to assert on ALL relevant fields**: After merging position sources, some fields may be overwritten or lost if the decoder does not handle nulls properly.
  - **Assuming null-safe field access**: The decoder or its helpers might return null or leave optional attributes unset; tests should explicitly check for `NullPointerException`-free access.
  - **Hardcoding single message scenarios**: Protocol decoders often handle variable-length messages; use parameterized tests to cover variations (e.g., only GPS, only LBS, both, partial).
  - **Not checking for protocol-specific edge cases**: Zero coordinates, missing length fields, unusual combinations of flags.

### Incorrect (too narrow) test approach:
```java
// Only tests GPS-only scenario — misses LBS merge and null safety
@Test
public void testDecodeGpsOnly() throws Exception {
    Gt06ProtocolDecoder decoder = new Gt06ProtocolDecoder(null);
    // ... send only GPS bytes
    Position position = decoder.decode(...);
    assertNotNull(position);
    assertEquals(48.123, position.getLatitude(), 0.001);
    // No checks on LBS fields — they might be null/invalid
}
```

### Correct (comprehensive) test approach:
```java
@ParameterizedTest
@CsvSource({
    "gps_and_lbs_hex,   48.123, 11.456, 262, 1, 100, 200",   // both sources present
    "gps_only_hex,      48.123, 11.456, 0,   0, 0,   0",       // only GPS
    "lbs_only_hex,      0.0,    0.0,    262, 1, 100, 200",     // only LBS
})
public void testDecodeWithPositionMerge(String msgType, double lat, double lon, 
        int mcc, int mnc, int lac, int cellId) throws Exception {
    Position position = decoder.decode(ctx, remoteAddress, getBytes(msgType));
    assertNotNull(position);
    assertEquals(lat, position.getLatitude(), 0.001);
    assertEquals(lon, position.getLongitude(), 0.001);
    
    // Access LBS attributes — must not throw NPE
    Object actualMcc = position.getAttributes().get(Position.KEY_MCC);
    Object actualMnc = position.getAttributes().get(Position.KEY_MNC);
    Object actualLac = position.getAttributes().get(Position.KEY_LAC);
    Object actualCell = position.getAttributes().get(Position.KEY_CELL);
    
    // These should be non-null (at worst zero for missing data)
    assertNotNull(actualMcc);
    assertNotNull(actualMnc);
    assertNotNull(actualLac);
    assertNotNull(actualCell);
}
```