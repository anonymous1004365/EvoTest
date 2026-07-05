---
name: protocol-decoder-state-and-type-validation
description: When testing protocol decoders with alternative parsing paths, verify
  that the final decoded state (attributes like speed, position, fuel) is correctly
  updated under all type bindings. This skill helps catch bugs where template-based
  parameter binding fails because of type mismatches between parameter names and expected
  types (e.g. CtTypeReference vs String).
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# protocol-decoder-state-and-type-validation

## Instructions

# Protocol Decoder: State & Type Validation on Alternative Paths

## Instructions

- WHEN the TG encounters a **protocol decoder** (e.g. `AplicomProtocolDecoder`) that has **multiple decoding paths** (e.g. an `if-else` or `switch` based on message type, where one path uses `TemplateBuilder` or template-based parameter binding),
- THEN it should verify that **all decoded attributes** (speed, position, fuel, power, etc.) are **correctly set to meaningful values** (not defaults, not null, not stale) **for each alternative path** — especially paths that rely on **template/parameter binding** where parameter names are matched to typed values.

- WHEN testing a protocol decoder's alternative path that uses `TemplateBuilder` with `bind(...)` calls,
- THEN the TG should ensure that **both `String`-typed and `CtTypeReference`-typed parameters** are tested for each bound value. Specifically:
  - Test that the decoder accepts and correctly binds parameter values regardless of whether the template parameter was registered by **name (String)** or by **type reference (CtTypeReference)**.
  - Verify that the resulting decoded object (e.g. `Position`) has **all expected attributes set** (e.g. `(Double) position.getAttributes().get(Position.KEY_FUEL)` should return the correct fuel value, not null).

- WHEN verifying the final decoded state (i.e. the `Position` object after decoding),
- THEN the TG should assert **specific expected values** for each attribute that was decoded:
  - e.g. `assertEquals(304.0, (Double) position.getAttributes().get(Position.KEY_FUEL), 0.01)`
  - e.g. `assertEquals(0.0, (Double) position.getAttributes().get(Position.KEY_POWER), 0.01)`
  - e.g. `assertEquals(0, position.getAttributes().get(Position.KEY_INDEX))`
  - Do NOT just assert that attributes are non-null — assert exact values that would expose a type-mismatch bug.

- **Common pitfalls to avoid**:
  - ❌ Testing only the **main/default path** and neglecting alternative decoding branches.
  - ❌ Testing only **String-typed parameter bindings** and missing `CtTypeReference`-based bindings that may behave differently.
  - ❌ Asserting only non-null or presence of attributes — this misses bugs where the value is the wrong type (e.g. a `CtTypeReference` object stored instead of the actual numeric value).
  - ❌ Assuming that because one path works (e.g. `decode with valid message type A`), another path (e.g. `message type B` with template binding) also works correctly.
  - ❌ Not inspecting the exact failure from the test runner — a `ClassCastException` or `wrong value` type may indicate a template type resolution bug.

### Correct Example (what the TG should write):
```java
// Test the alternative decoding path with template-based parameter binding
// where parameters may be bound by type reference (CtTypeReference) rather than name (String)
@Test
public void testDecodeWithTemplateBinding() throws Exception {
    AplicomProtocolDecoder decoder = new AplicomProtocolDecoder(null);
    // Provide a message that triggers the alternative path (template binding approach)
    // ... set up channel, remoteAddress, msg ...
    Position position = (Position) decoder.decode(channel, remoteAddress, msg);
    
    // Verify ALL expected attributes with exact values
    assertEquals(304.0, (Double) position.getAttributes().get(Position.KEY_FUEL), 0.01);
    assertEquals(0.0, (Double) position.getAttributes().get(Position.KEY_POWER), 0.01);
    assertEquals(0, position.getAttributes().get(Position.KEY_INDEX));
}
```

### Incorrect Example (common mistake without this skill):
```java
// BUG: Does not exercise the alternative template-based binding path
// Only tests the standard path, missing type-mismatch bugs
@Test
public void testDecode() throws Exception {
    AplicomProtocolDecoder decoder = new AplicomProtocolDecoder(null);
    Position position = (Position) decoder.decode(channel, remoteAddress, msg);
    
    // WRONG: Only checks that attributes exist, not their actual values
    assertNotNull(position.getAttributes().get(Position.KEY_FUEL));
    assertNotNull(position.getAttributes().get(Position.KEY_POWER));
    
    // BUG: This would pass even if fuel was set to a CtTypeReference object instead of a Double
}
```