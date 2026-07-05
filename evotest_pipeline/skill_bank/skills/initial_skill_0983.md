---
name: isodatetime-parse-fallback-validation
description: When parsing ISO date/time string values (like PostgreSQL timestamps)
  that may have varying fractional-second precision, validate that all expected formats,
  including edge cases with zero/NULL fractional seconds, are correctly handled without
  falling back to wrong types.
code_tags:
- VALIDATION
- DATETIME_PARSE_FORMAT
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# isodatetime-parse-fallback-validation

## Instructions

# ISO DateTime Parse Fallback Validation

## Instructions

- WHEN the TG encounters code that parses ISO 8601 date/time string values using multiple format patterns or multiple `DateTimeFormatter` instances (especially for timestamps with variable fractional-second precision),  
  THEN it should write **parametric tests** that exercise **every supported format variant**, including edge cases such as:
  - Timestamps with no fractional seconds (e.g., `"2021-03-19T10:12:05"`)
  - Timestamps with zero fractional seconds (e.g., `"2021-03-19T10:12:05.000000"`)
  - Timestamps with partial fractional seconds (e.g., `"2021-03-19T10:12:05.1"`, `"2021-03-19T10:12:05.123"`)
  - Timestamps with full microsecond precision (e.g., `"2021-03-19T10:12:05.123456"`)
  - Timestamps with timezone offsets (e.g., `"2021-03-19T10:12:05Z"`, `"2021-03-19T10:12:05+00:00"`)
  - Verify that the returned value is of the expected type (e.g., `OffsetDateTime`, `LocalDateTime`, `Instant`) — **not** accidentally downcast to `LocalDateTime` when the string contains a zone offset.
  - Use an assertion that compares the parsed value with the expected parsed value using `assertEquals(expected, actual)`, not just string comparison.

- WHEN the parsing logic has multiple fallback `try-catch` blocks that try different formats in sequence,  
  THEN the TG should test the **first attempted format with a value that only matches a later format** — this reveals whether early fallback catches produce incorrect results without throwing.

- Common pitfalls to avoid:
  - **Testing only the happy path** (one format) and missing the secondary format that causes the bug.
  - **Testing only `String` inputs** but not verifying the **type** of the parsed result (e.g., `OffsetDateTime` vs `LocalDateTime`).
  - **Assuming that any non-null result from a parse attempt is correct** — the fix may require narrowing the catch to avoid swallowing format mismatches.
  - **Not testing values with zero fractional seconds** (`"` 00`000000"`) — these often take a different code path than non-zero values.

### Correct example (detects the bug)

```java
@ParameterizedTest
@ValueSource(strings = {
    "2021-03-19T10:12:05",
    "2021-03-19T10:12:05.000000",
    "2021-03-19T10:12:05.123456",
    "2021-03-19T10:12:05Z",
    "2021-03-19T10:12:05.000000Z",
    "2021-03-19T10:12:05.123456Z"
})
void testTimestampParsing(String input) {
    // Should not throw and should return a consistent type
    Object result = MyParser.parseTimestamp(input);
    assertNotNull(result);
    assertTrue(result instanceof OffsetDateTime || result instanceof Instant,
        "Expected OffsetDateTime or Instant for: " + input);
}
```

### Incorrect example (misses the bug)

```java
@Test
void testTimestamp() {
    // Only tests one format — does not exercise the zero-fractional-seconds edge case
    Object result = MyParser.parseTimestamp("2021-03-19T10:12:05.123456");
    assertNotNull(result);
}
```