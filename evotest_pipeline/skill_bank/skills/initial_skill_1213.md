---
name: alternative-protocol-decoding-pattern
description: When decoding protocol frames with alternative (alt) sub-protocols that
  produce negative values for fields normally expected to be positive, the TG must
  test both the normal AND alternative decoding paths to ensure boundaries (e.g.,
  non-negative checks) are consistent across both formats.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-pattern

## Instructions

# Alternative Protocol Decoding with Boundary Violations

## Instructions

- WHEN the TG encounters a protocol decoder that switches between two or more frame formats based on a flag byte / prefix / discriminator (e.g., `alt` boolean, `type` byte), THEN the TG must write separate test cases for EACH format, not just the primary/default one.

- WHEN one of the alternative formats can encode a field (e.g., `speed`, `course`, `altitude`) as a negative or sentinel value (e.g., `-1` for unavailable GPS fix) that the primary format never produces, THEN the TG must:
  1. Construct a full protocol frame (byte array / string) that triggers the alternative path.
  2. Ensure the alternative path is exercised (e.g., `alt=true` or a discriminator byte is set).
  3. Assert that fields that must be non-negative in the primary format are handled correctly (e.g., clamped to `0`, left as-is, or left as `null` / missing).

- WHEN the protocol decoder contains a chain of `try { … } catch (RuntimeException e) { … }` that silently swallows exceptions from one branch, THEN the TG must assert that the alternative branch returns expected values AND does not throw or get silently caught by the catch-all.

- Common pitfalls to avoid:
  - Testing only the primary/default decoding path while the bug lives in the alternative path.
  - Assuming all fields are positive in all formats — test explicit negative/sentinel values in the alternative format.
  - Writing a single test that covers only one discriminator value; use a parametrized test that iterates over all discriminator values (e.g., `alt=true` and `alt=false`).

### Correct Example (JUnit5 style)

```java
@ParameterizedTest
@CsvSource({
    "false, 10,  0.5",   // primary path
    "true,   5, -1.0"    // alternative path, negative value
})
void testDecodeWithMixedFormats(boolean alt, int speedRaw, double expectedSpeed) {
    byte[] frame = buildFrame(alt, speedRaw);
    Position pos = decoder.decode(frame);
    assertEquals(expectedSpeed, pos.getSpeed(), 0.001);
}
```

### Incorrect Example (only tests the happy primary path)

```java
@Test
void testDecodePrimary() {
    byte[] frame = buildFrame(false, 10);
    Position pos = decoder.decode(frame);
    assertEquals(10.0, pos.getSpeed(), 0.001);
    // BUG: alt=true with negative speed is never tested
}
```