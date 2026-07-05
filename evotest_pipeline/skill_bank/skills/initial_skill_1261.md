---
name: null-check-after-byte-parse
description: WHEN the TG encounters code that parses raw byte data (e.g., from Bluetooth
  sensors, protocol messages, or network streams) and the parsed values are passed
  into constructors or factory methods, THEN the TG must test that null values returned
  from parsing methods are properly handled, particularly when those values are used
  to set object state or are passed to validation methods. This skill helps prevent
  NullPointerExceptions that occur when protocol payloads contain structurally valid
  but semantically incomplete data.
code_tags:
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# null-check-after-byte-parse

## Instructions

# Null Check After Byte Parse

## Instructions

WHEN the TG encounters code that:
1. Reads and parses raw byte data from a protocol message (e.g., Bluetooth advertisement packets, network frames, or sensor payloads)
2. Extracts sub-components from the parsed data (e.g., temperature, humidity, battery level, or device state fields)
3. Passes those extracted values to constructors, setters, or factory methods that create domain objects
4. Has a method that validates parsed data before constructing the domain object

THEN the TG should:
1. Create a test case where the raw byte payload is structurally valid (correct length, correct format) BUT one or more extracted sub-field values are null/zero/missing
2. Verify that the parsing code does NOT throw a NullPointerException when constructing the domain object with the null/missing field
3. Verify that the validation method correctly rejects the incomplete payload (e.g., returns false, throws IllegalArgumentException, logs an error)
4. Do NOT merely test with a completely empty or malformed byte array — the payload should be well-formed enough to pass the initial format check but incomplete in a specific sub-field

Common pitfalls to avoid:
- Testing only fully valid payloads — this misses bugs where missing sub-fields cause NPEs
- Testing only completely malformed payloads (wrong length, wrong header) — this misses bugs where format is valid but content is incomplete
- Forgetting to test with payloads that are just barely valid enough to pass initial format checks but fail on specific field extractions
- Assuming that if a parsing method returns null/missing for a field, downstream code handles it gracefully — always verify explicitly

### Correct example (Java/JUnit):
```java
@Test(expected = NullPointerException.class)
public void testDecodeWithMissingBatteryThrowsNPE() {
    // Payload format is valid (correct length, correct header) 
    // but battery field is missing/null
    byte[] payload = new byte[] {0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00};
    WatchProtocolDecoder decoder = new WatchProtocolDecoder();
    // This should NOT throw NPE — it should handle gracefully
    decoder.decode(payload);
}
```

### Incorrect example (incomplete testing):
```java
@Test
public void testDecode() {
    // Only testing fully valid payload — missing null handling test
    byte[] payload = new byte[] {0x00, 0x01, 0x02, (byte)0x64, (byte)0x03, 0x00, 0x01, 0x00};
    WatchProtocolDecoder decoder = new WatchProtocolDecoder();
    Object result = decoder.decode(payload);
    assertNotNull(result);
}
```