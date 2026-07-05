---
name: protocol-decoder-array-string-mismatch
description: When a protocol decoder uses string splitting (split()) to parse comma-separated
  fields into arrays, the TG should test with fields that contain both String and
  numeric-String values to catch array index issues caused by empty trailing elements
  after split(). The triggering test (IntellitracProtocolDecoder) uses split() on
  comma-delimited input, which can produce unexpected array lengths when trailing
  commas or empty strings are present.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-array-string-mismatch

## Instructions

# Protocol Decoder Array Index from String Split

## Instructions

- WHEN the TG encounters a protocol decoder that splits a comma-separated or delimiter-separated string (using `String.split(",")` or similar), AND the decoder parses the resulting array elements by index (e.g., `arr[0]`, `arr[1]`, etc.):
  - THEN the TG MUST write a parametric test that verifies the decoder correctly handles inputs where the delimiter-separated string contains trailing or leading empty segments (e.g., a trailing comma producing an empty-string element in the split array).
  - Specifically: test with input strings that have fields of different types (String, numeric String, etc.) and ensure each field is decoded to the correct type. For fields expected to be numeric (e.g., speed, course), test that they are properly parsed (e.g., using `Double.parseDouble()` or `Integer.parseInt()`) and are not silently interpreted as zero or null when the actual value is valid.
  - The test MUST verify that no `ArrayIndexOutOfBoundsException` occurs on the buggy version due to unexpected array size from split.
  - Include test cases that exercise ALL code paths in the decoder — not just the primary/popular path. For decoders with branching logic based on string content (e.g., different message formats), write separate test cases for each distinct format.
  - Common pitfall: testing only with well-formed input that produces the expected array length. Always test with inputs that could produce a shorter array (e.g., missing fields, trailing commas, extra commas).
  - Example: `"123456789012345,2022-01-01,12:00:00,10.5,20.3,30.0,45.0"` — if split produces 7 elements but decoder accesses index 7 or higher, an `ArrayIndexOutOfBoundsException` will occur on the buggy version.

- WHEN the TG encounters a test class for a protocol decoder (e.g., `IntellitracProtocolDecoderTest`):
  - THEN the TG MUST verify that the test provides coverage over the full range of message formats the decoder accepts, not just the most common one.
  - Include tests that exercise alternative/less common message formats.
  - Common pitfall: stopping at one test method when the decoder supports multiple message formats that each need their own test case.