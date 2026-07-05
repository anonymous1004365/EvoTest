---
name: configuration-gated-field-parsing
description: When a boolean configuration flag (like `hbm`) gates the parsing of certain
  message fields, the test must verify behavior for both flag-on and flag-off cases,
  especially checking that remaining fields are not misaligned or silently skipped
  when the flag is off.
code_tags:
- BOUNDARY_CHECK
- NULL_CHECK
- VALIDATION
- CONFIGURATION_GATED_BEHAVIOR
test_pattern: STATE_TEST
---

# configuration-gated-field-parsing

## Instructions

# Configuration-Gated Field Parsing

## Instructions

- WHEN the TG encounters a protocol decoder (e.g., `SuntechProtocolDecoder`) that reads a boolean configuration property (like `hbm`) from `Context.getConfig().getBoolean(...)` and uses it to conditionally parse position fields (e.g., `Position.KEY_HOURS`, `Position.KEY_BATTERY`)
- THEN the TG must write separate test cases for BOTH configurations — one test case where the config flag is `true` (fields should be parsed) AND one where the config flag is `false` (fields should NOT be parsed). The test should use a test input that contains all possible fields (including the gated ones) and verify:
  - When the flag is `true`: all gated positional fields are correctly set on the result (`Position.KEY_HOURS`, `Position.KEY_BATTERY`)
  - When the flag is `false`: the gated fields are NOT set on the result, but the message parsing must NOT throw an `ArrayIndexOutOfBoundsException` or silently corrupt remaining fields
- WHEN the TG encounters `if (index < values.length)` guards for gated field parsing that are wrapped inside a config-conditional block, verify that the condition check correctly protects against index overruns both inside and outside the config block
- Common pitfalls:
  - Testing only the flag-on (true) case and assuming the decoder works for flag-off (false) — the buggy code skipped KEY_HOURS and KEY_BATTERY parsing when hbm=false, which is correct, but other parts of the code may misbehave when the config flag is absent
  - Assuming that the config flag only adds fields (making them "optional extra") but failing to check that the rest of the parsing pipeline remains correct when those fields are absent from the message
  - Not simulating both config states: use a configuration mechanism (e.g., set a system property or mock `Context.getConfig().getBoolean()`) to toggle the flag between test runs

### Correct Example (should detect the bug):
```java
@Test
public void testDecodeWithHbmTrue() {
    SuntechProtocolDecoder decoder = new SuntechProtocolDecoder(new SuntechProtocol());
    // Assume configuration sets hbm=true for this test
    Position position = decoder.decode(null, null, "<message with hours and battery fields>");
    assertNotNull(position);
    assertNotNull(position.getAttributes().get(Position.KEY_HOURS));
    assertNotNull(position.getAttributes().get(Position.KEY_BATTERY));
}

@Test
public void testDecodeWithHbmFalse() {
    SuntechProtocolDecoder decoder = new SuntechProtocolDecoder(new SuntechProtocol());
    // Assume configuration sets hbm=false for this test
    Position position = decoder.decode(null, null, "<same message>");
    assertNotNull(position);
    assertNull(position.getAttributes().get(Position.KEY_HOURS));
    assertNull(position.getAttributes().get(Position.KEY_BATTERY));
}
```

### Incorrect Example (misses the bug):
```java
@Test
public void testDecode() {
    SuntechProtocolDecoder decoder = new SuntechProtocolDecoder(new SuntechProtocol());
    Position position = decoder.decode(null, null, "<message>");
    // Only checks happy path, skips the hbm=false scenario
    assertNotNull(position);
}
```