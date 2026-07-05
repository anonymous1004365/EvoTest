---
name: empty-string-guard-before-parse
description: When parsing string tokens from device protocol data using Integer.parseInt,
  Double.parseDouble, or similar parsing methods, the TG must test with empty string
  values that could appear in real device data, not just with null values.
code_tags:
- EMPTY_STRING_PARSING
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# empty-string-guard-before-parse

## Instructions

# Guard Against Empty String Before Parsing

## Instructions

- WHEN the TG encounters code that parses string tokens/values from a data array (e.g., `data[i]`, `parts[j]`, or similar tokenized input) using methods like `Integer.parseInt(...)`, `Double.parseDouble(...)`, `Long.parseLong(...)`, `Short.parseShort(...)`, or `Float.parseFloat(...)` — especially within a `switch` statement or conditional block processing protocol fields (e.g., `"#LAC#"`, `"#CID#"`, `"#EDT#"`, etc.)
- THEN the TG should test with an empty string `""` as one of the data values to ensure the code handles it gracefully without throwing `NumberFormatException`
- Include test cases that send an input where one of the parsed tokens is `""` (empty string), and verify that no exception is thrown — the method should either skip the empty value or continue processing normally
- Common pitfalls to avoid:
  - Testing only with `null` values — empty string `""` is a different case and `Integer.parseInt("")` throws `NumberFormatException` while `null` would cause `NullPointerException`. Both need separate handling.
  - Assuming all tokens in the data array will always be non-empty — real-world protocol data can have empty fields, especially at the end of a message or when a device sends incomplete data.
  - Adding only a single guard at the beginning of a `for` loop — the TG must check each `Integer.parseInt(...)` call individually, as each parsing operation is a separate risk point.

## Example (correct)
```java
// Device sends: "#LAC#,#CID#," where the last field is empty
// Expected: should skip parsing empty string, not throw NumberFormatException
@Test
void testDecodeWithEmptyFields() throws Exception {
    StarLinkProtocolDecoder decoder = new StarLinkProtocolDecoder(null);
    // Minimal test setup for device protocol decoder test
    String testData = "...";  // data where one token field is empty string
    // Verify no exception is thrown
    assertDoesNotThrow(() -> decoder.decode(null, null, testData));
}
```

## Example (incorrect — missing empty string test)
```java
// BUGGY: Only tests null values, misses the empty string case
@Test
void testDecodeWithNullFields() throws Exception {
    // This test passes even with the buggy code because null != ""
    // It does NOT catch BugId-003 where "" causes NumberFormatException
    ...
}
```