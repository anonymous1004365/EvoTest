---
name: iso-date-time-fallback-parsing
description: When code parses ISO date/time strings with a primary formatter and falls
  back to an alternative formatter, the fallback branch may throw exceptions on valid
  inputs. This skill teaches how to test that both the primary and fallback parsing
  branches correctly handle standard ISO date/time values.
code_tags:
- DATE_FORMAT_PARSING
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# iso-date-time-fallback-parsing

## Instructions

# ISO DateTime Fallback Parsing

## Instructions

- WHEN the TG encounters code that parses date/time strings using a primary `DateTimeFormatter` (e.g., `DateTimeFormatter.ISO_INSTANT` or `DateTimeFormatter.ISO_OFFSET_DATE_TIME`) and catches a `DateTimeParseException` to fall back to an alternative formatter (e.g., `DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")` or similar)
- THEN the TG should write a test that:
  1. Constructs a date/time string that conforms to the **primary** format (e.g., `"2024-01-15T10:30:00Z"` for `ISO_INSTANT`)
  2. Calls the parsing method with this input
  3. Verifies that parsing succeeds without throwing **any** exception
  4. Also tests with a date/time string that conforms to the **fallback** format (e.g., `"2024-01-15T10:30:00.000Z"` for a pattern expecting fixed milliseconds)
  5. Verifies that the fallback path also returns a valid result
- Common pitfalls to avoid:
  - Testing only the primary path (happy path) and never exercising the fallback parsing branch
  - Assuming that if a string looks like ISO format, the fallback formatter can parse it — the fallback pattern may be more restrictive (e.g., requiring exactly 3 digits of milliseconds) while the primary accepts more flexible inputs (e.g., `ISO_INSTANT` accepts both `"2024-01-15T10:30:00Z"` and `"2024-01-15T10:30:00.123Z"`)
  - Not testing edge cases such as date/time strings with fractional seconds of varying lengths (0, 1, 2, 3, 6, 9 digits) against the fallback formatter
  - Forgetting to test the case where the fallback parser is used on a string that was actually intended for the primary parser, causing a `DateTimeParseException` to be thrown from the fallback branch (which is **not** caught, leading to test failure)

### Correct Example (pseudocode)
```java
@Test
void testDateParsingWithFallback() {
    // Test primary path - ISO_INSTANT without fractional seconds
    String input1 = "2024-01-15T10:30:00Z";
    assertDoesNotThrow(() -> parser.parseDate(input1));
    
    // Test fallback path - pattern with exactly 3 fractional seconds
    String input2 = "2024-01-15T10:30:00.123Z";
    assertDoesNotThrow(() -> parser.parseDate(input2));
    
    // Test fallback path - pattern with 0 fractional seconds but fallback requires 3 digits
    // This may fail if the fallback formatter is too strict
    String input3 = "2024-01-15T10:30:00.000Z";
    assertDoesNotThrow(() -> parser.parseDate(input3));
}
```

### Incorrect Example (pseudocode)
```java
@Test
void testDateParsing() {
    // ONLY tests the primary path - misses fallback bugs entirely
    String input = "2024-01-15T10:30:00Z";
    assertEquals(expected, parser.parseDate(input));
    
    // Missing test for: "2024-01-15T10:30:00.000Z" which exercises the fallback
    // On the buggy version, the fallback formatter may throw DateTimeParseException
}
```