---
name: ulbotech-protocol-string-value-decoding
description: When decoding protocol messages with string parameters that may have
  overloaded types (e.g., both String and numeric), the TG should test with mixed-type
  parameter values to catch ClassCastException or type-mismatch bugs. This skill applies
  to protocol decoder classes like UlbotechProtocolDecoder.
code_tags:
- STATE_MUTATION
- NULL_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# ulbotech-protocol-string-value-decoding

## Instructions

# Ulbotech Protocol String Value Decoding

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `UlbotechProtocolDecoder`) that decodes message parameters by iterating over keys and retrieving values from a data structure (e.g., a `Map<String, Object>` or similar),
- THEN the TG should test with at least one parameter whose value is **not a String** but another type (e.g., `Long`, `Integer`, `Double`, `Boolean`, or `CtTypeReference`), to verify that the decoder correctly handles non-String types without throwing a `ClassCastException`.
  - Specifically, look for patterns where the decoder does something like `(String) map.get(key)` or `String.valueOf(map.get(key))` or similar unchecked casts.
  - If the buggy version fails with a `ClassCastException` when a non-String value is encountered, the test should expect that exception or verify graceful handling.
  - Include at least one test case where a parameter value is a `String` AND at least one where it is a non-String (e.g., `Long.valueOf(12345)`).
  - The test should verify that the decoder completes without throwing an unexpected type-related exception.

- Common pitfalls:
  - Testing only with `String` type parameter values, which would not trigger the bug.
  - Assuming all values in the parameter map are `String` types.
  - Not testing with `Long` or `Integer` values in addition to `String` values.
  - Catching `ClassCastException` but not reproducing the exact failure scenario (e.g., missing the specific parameter key that causes the cast).

- Example (correct):
``java
  Map<String, Object> params = new HashMap<>();
  params.put("key1", "value1");
  params.put("key2", Long.valueOf(123)); // non-String value
  // Expected: decoder should handle this without ClassCastException
  // Buggy version might throw: java.lang.ClassCastException: java.lang.Long cannot be cast to java.lang.String
  assertThrows(ClassCastException.class, () -> decoder.decode(msg));
``

- Example (incorrect — would NOT catch the bug):
``java
  Map<String, Object> params = new HashMap<>();
  params.put("key1", "value1");
  params.put("key2", "value2"); // Both are String — bug not triggered
  decoder.decode(msg); // Always passes, never reveals the bug
``