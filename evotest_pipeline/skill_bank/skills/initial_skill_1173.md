---
name: protocol-decoder-input-validation
description: When writing tests for protocol decoders, validate that they handle both
  expected and unexpected/boundary input data correctly. Tests should exercise multiple
  message formats, partial data, and type variations to ensure robustness against
  malformed or unexpected input.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-input-validation

## Instructions

# Protocol Decoder Input Validation

## Instructions

**WHEN** the TG encounters a protocol decoder class (e.g., `GpsMarkerProtocolDecoder`) or any class that decodes/parses raw byte data or string messages into structured objects:

- **THEN** the TG should write tests that exercise the decoder with **multiple distinct inputs** including:
  - Different message types/formats that the decoder might support (e.g., different frame IDs, different data payload formats)
  - Boundary values for numeric fields (e.g., 0, negative values, maximum values)
  - Edge case payload lengths (empty payloads, extremely short payloads, padding variations)

- **THEN** the TG should use a **parameterized test pattern** (e.g., JUnit's `@ParameterizedTest` with `@CsvSource`, `@MethodSource`, or `@ValueSource`) to systematically test multiple input variations.

- **THEN** the TG should ensure the test verifies the decoder does NOT throw unexpected exceptions (like `ArrayIndexOutOfBoundsException`, `NullPointerException`, `IndexOutOfBoundsException`) on malformed or boundary inputs. When the buggy version throws such exceptions, the test should assert that the fixed version handles them gracefully (e.g., by returning `null`, returning a partial decode, or throwing a domain-appropriate exception).

- **Common pitfalls to avoid:**
  - Testing only a single "happy path" input — this misses bugs that only surface with alternative message formats or edge cases.
  - Testing only `String`-type inputs when the decoder also accepts other types (e.g., `byte[]`, `CtTypeReference`, protocol buffer objects).
  - Not testing with empty/missing optional fields in the message.
  - Assuming the decoder will always receive complete, well-formed messages.
  - Testing only the protocol framing level without testing the decoder's actual decode logic.

## Correct Example (Parameterized Test)

```java
@ParameterizedTest
@CsvSource({
    "0102030405060708, 1, default",   // Standard message format
    "0102030405060708, 2, custom",    // Alternative message format with different frame ID
    "0102030405060708, 0, unknown",   // Edge: frame ID 0
    "0102030405060708, -1, invalid",  // Edge: negative frame ID
    ", 1, default",                   // Edge: empty payload
    "01, 1, truncated"               // Edge: too-short payload
})
void testDecodeVariousInputs(String hexPayload, int frameId, String expectedType) {
    GpsMarkerProtocolDecoder decoder = new GpsMarkerProtocolDecoder();
    // Decode should not throw exceptions for any of these inputs
    assertDoesNotThrow(() -> {
        Object result = decoder.decode(hexPayload, frameId);
        // If decode returns null, test should not fail on null
        if (result != null) {
            // Additional assertions on result if non-null
        }
    });
}
```

## Incorrect Example (Only Happy Path)

```java
@Test
void testDecode() {
    GpsMarkerProtocolDecoder decoder = new GpsMarkerProtocolDecoder();
    // Only tests one specific input — misses bugs in alternative decode paths
    Object result = decoder.decode("0102030405060708", 1);
    assertNotNull(result);
    // Does not test with:
    // - Different frame IDs
    // - Boundary numeric values
    // - Truncated or empty payloads
    // - Type variations (String vs CtTypeReference)
}
```