---
name: configuration-flag-gated-parsing
description: WHEN a protocol decoder reads a boolean configuration flag from Context.getConfig().getBoolean()
  that gates which message fields are parsed and set on the Position object, THEN
  the TG should test both configurations (flag=true and flag=false) to ensure the
  conditional field parsing behaves correctly — the bug is that the KEY_HOURS and
  KEY_BATTERY fields were unconditionally parsed before the fix, but should only be
  parsed when the hbm flag is true.
code_tags:
- CONFIGURATION_FLAG_BEHAVIOR
- CONDITIONAL_EXECUTION
test_pattern: PARAMETRIC_TEST
---

# configuration-flag-gated-parsing

## Instructions

# Configuration Flag-Gated Field Parsing

## Instructions

WHEN the TG encounters a protocol decoder that reads a boolean configuration flag (from `Context.getConfig().getBoolean(...)`) and uses it to conditionally gate field parsing logic (wrapping field assignments inside `if (flag) { ... }` blocks):

- THEN the TG should create a parametric test that exercises both configurations (flag=true and flag=false) to verify the conditional behavior.
- Concrete example: In `SuntechProtocolDecoder`, the `hbm` flag controls whether `Position.KEY_HOURS` and `Position.KEY_BATTERY` are parsed from the message. With `hbm=false`, those fields must NOT be set on the Position. With `hbm=true`, they MUST be set.
- The TG should verify that when the flag is false, the Position object does NOT contain the gated keys (e.g., `assertNull(position.getAttributes().get(Position.KEY_HOURS))` and `assertNull(position.getAttributes().get(Position.KEY_BATTERY))`).
- The TG should verify that when the flag is true, the Position object DOES contain those keys with the expected parsed values.
- Common pitfalls:
  - Testing only the default configuration (flag=true or flag=false) and missing the alternate path.
  - Assuming that fields were always parsed before (the buggy behavior) and not noticing the new conditional guard.
  - Forgetting to reset/mock the configuration between test cases so the flag value carries over incorrectly.
  - Testing with message data that doesn't have enough fields to exercise the index checks inside the flag block.

## Examples

Correct test pattern (parametric, testing both flag states):

```java
// Parametric test for hbm flag behavior
@Test
public void testDecodeWithHbmDisabled() {
    // Arrange: set hbm=false in config
    when(Context.getConfig().getBoolean(eq("suntech.hbm"))).thenReturn(false);
    SuntechProtocolDecoder decoder = new SuntechProtocolDecoder(protocol);
    
    // Act: decode a message that has hour and battery fields
    Position position = decoder.decode(null, null, "content with hours and battery");
    
    // Assert: hbm=false, so KEY_HOURS and KEY_BATTERY must NOT be set
    assertNull(position.getAttributes().get(Position.KEY_HOURS));
    assertNull(position.getAttributes().get(Position.KEY_BATTERY));
}

@Test
public void testDecodeWithHbmEnabled() {
    // Arrange: set hbm=true in config
    when(Context.getConfig().getBoolean(eq("suntech.hbm"))).thenReturn(true);
    SuntechProtocolDecoder decoder = new SuntechProtocolDecoder(protocol);
    
    // Act: decode the same message
    Position position = decoder.decode(null, null, "content with hours and battery");
    
    // Assert: hbm=true, so KEY_HOURS and KEY_BATTERY must be set
    assertNotNull(position.getAttributes().get(Position.KEY_HOURS));
    assertNotNull(position.getAttributes().get(Position.KEY_BATTERY));
    assertEquals(expectedHours, position.getAttributes().get(Position.KEY_HOURS));
    assertEquals(expectedBattery, position.getAttributes().get(Position.KEY_BATTERY));
}
```

Incorrect pattern (testing only one configuration):

```java
// BAD: Only tests the default (or one) configuration path
@Test
public void testDecode() {
    // Does not set hbm flag at all — defaults may vary
    SuntechProtocolDecoder decoder = new SuntechProtocolDecoder(protocol);
    Position position = decoder.decode(null, null, "content...");
    
    // Does not check which fields are present/absent
    assertNotNull(position);
    // Missing assertions about KEY_HOURS and KEY_BATTERY presence
}
```