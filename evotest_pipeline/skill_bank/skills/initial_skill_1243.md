---
name: alternative-protocol-decoding-path
description: When a protocol decoder has multiple alternative decoding paths (e.g., different frame types or parsing strategies), errors in one path can cause silent failures or incorrect behavior. This skill teaches testers to explicitly test each alternative path with both valid and boundary inputs.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder class that handles multiple message/frame types (e.g., via type codes, frame headers, or conditional parsing branches)
- THEN it should create parametric tests that exercise each distinct decoding branch with appropriate input data. For each alternative path, the test must send a message that triggers that specific path and verify:
  1. The decoder does NOT throw an unexpected exception (e.g., `IndexOutOfBoundsException`, `NullPointerException`, `NumberFormatException`)
  2. The decoded result contains the correct values (e.g., position data such as latitude, longitude, speed, time) matching the expected format for that message type
  3. Edge cases within each path: missing optional fields, truncated data, boundary values for numeric fields
- Common pitfalls to avoid:
  - **Testing only the happy path**: Do not assume the primary/first message type works — each alternative path may have its own bugs (e.g., off-by-one in field offsets, wrong delimiter handling, type conversion errors)
  - **Ignoring null/invalid fields**: When an alternative path does not populate certain fields (e.g., course, speed, altitude), verify they remain as default values (0, null) rather than containing leftover/uninitialized data
  - **Assuming field order consistency**: Different message types may encode fields in different order or with different separators — test each path independently with its own expected field positions
  - **Not testing protocol version variations**: If the decoder handles different protocol versions, each version may change field offsets, types, or required fields

### Correct Example (for a protocol with type codes 0x01 and 0x02):

```java
@Test
public void testProtocolDecodeMultipleTypes() {
    GotopProtocolDecoder decoder = new GotopProtocolDecoder(null);
    
    // Type 0x01: Full position report
    String msg1 = "0101,861234567890123,123456.000,A,2234.5678,N,11400.1234,E,0.5,45.2,100321";
    Position pos1 = decoder.decode(null, null, msg1);
    assertNotNull(pos1);
    assertEquals(22.57613, pos1.getLatitude(), 0.001);
    assertEquals(114.002057, pos1.getLongitude(), 0.001);
    assertEquals(45.2, pos1.getSpeed(), 0.1);
    
    // Type 0x02: Minimal position report (no speed/altitude)
    String msg2 = "0202,861234567890123,123456.000,A,2234.5678,N,11400.1234,E";
    Position pos2 = decoder.decode(null, null, msg2);
    assertNotNull(pos2);
    assertEquals(22.57613, pos2.getLatitude(), 0.001);
    assertEquals(114.002057, pos2.getLongitude(), 0.001);
    assertEquals(0.0, pos2.getSpeed(), 0.0); // default for missing field
}
```

### Incorrect Example (only tests the primary type):

```java
@Test
public void testDecode() {
    GotopProtocolDecoder decoder = new GotopProtocolDecoder(null);
    // Only tests type 0x01 — type 0x02 may throw or produce wrong data
    String msg = "0101,861234567890123,123456.000,A,2234.5678,N,11400.1234,E,0.5,45.2,100321";
    Position pos = decoder.decode(null, null, msg);
    assertNotNull(pos);
}
```