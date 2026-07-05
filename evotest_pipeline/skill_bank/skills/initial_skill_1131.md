---
name: protocol-decoder-odometer-attribute-set-null
description: Use when a protocol decoder conditionally sets a Position attribute (like
  KEY_ODOMETER). Tests should verify that the attribute is properly set when data
  is present and NOT set (or left as default) when data is absent, guarding against
  null values being written.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# protocol-decoder-odometer-attribute-set-null

## Instructions

# Protocol Decoder Odometer Attribute Null Guard

## Instructions

- WHEN a protocol decoder sets a Position attribute (e.g., `position.set(Position.KEY_ODOMETER, ...)`) based on a parsed value from a protocol message (e.g., using `parser.next()` to get a `String` which is then converted to a `long` or `double`)
- THEN the test must verify the behavior for both the case where the value IS present in the message AND the case where it is NOT present (i.e., when the parser returns null or an empty/absent value). Specifically, test that a null or missing parsed value does NOT result in the attribute being set on the Position object (e.g., `position.getAttributes().get(Position.KEY_ODOMETER)` should be null or the attribute should not be in the map).
- Include concrete values like the exact attribute key name (`Position.KEY_ODOMETER`, which is `"odometer"`) and the method call pattern (e.g., `String value = parser.next(); if (value != null) { position.set(Position.KEY_ODOMETER, ...); }`). The test should use a binary protocol buffer that omits the odometer field and assert that calling `decoder.decode(...)` does not throw a `NullPointerException` and that the resulting position's `KEY_ODOMETER` attribute remains unset.
- Common pitfalls to avoid: (1) Providing only test data where the odometer is present (i.e., only the "happy path"), missing the null/missing case entirely. (2) Assuming that because `parser.next()` would return null, subsequent code handles it gracefully — the bug shows it can throw a `NullPointerException` or silently set a bad value. (3) Relying on exception-based testing (expecting an exception) when the actual bug is silently corrupting position data with a null/missing value.

**Correct example (would catch this bug):**
```java
// Test message without odometer field
String msgWithoutOdometer = "*HQ,123456789012345,V1,012345.000,A,2234.5678,N,12345.6789,E,0.00,0,0.0,0,00000000,,0#";
Position position = decoder.decode(null, null, msgWithoutOdometer);
assertNotNull(position);
assertNull(position.getAttributes().get(Position.KEY_ODOMETER));
// Test message with odometer field
String msgWithOdometer = "*HQ,123456789012345,V1,012345.000,A,2234.5678,N,12345.6789,E,0.00,0,0.0,0,00000000,,100#";
Position position2 = decoder.decode(null, null, msgWithOdometer);
assertNotNull(position2);
assertEquals(100.0, position2.getAttributes().get(Position.KEY_ODOMETER));
```

**Incorrect example (would miss this bug):**
```java
// Only tests the case where odometer is present
String msg = "*HQ,123456789012345,V1,012345.000,A,2234.5678,N,12345.6789,E,0.00,0,0.0,0,00000000,,100#";
Position position = decoder.decode(null, null, msg);
assertNotNull(position);
assertEquals(100.0, position.getAttributes().get(Position.KEY_ODOMETER));
// Missing the null/missing odometer case entirely
```