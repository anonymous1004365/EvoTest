---
name: regex-fallback-optional-pattern-fields
description: When decoding protocol messages with optional fields, test that the decoder
  correctly handles missing/absent values by ensuring the regex pattern uses optional
  quantifiers (?, *) rather than requiring mandatory digits. Use this skill when the
  decoder uses PatternBuilder with .number() calls that may not always be present.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# regex-fallback-optional-pattern-fields

## Instructions

# Regex Fallback and Optional Pattern Field Decoding

## Instructions

WHEN the TG encounters a protocol decoder that parses GPS tracking messages with `.number()`, `.text()`, and `.groupBegin()/.groupEnd()` calls in a `PatternBuilder`, and the test involves `Parser` and `Position` objects from a protocol library like `org.traccar`:

- THEN the TG should identify fields in the pattern that may be absent (optional) in the actual messages. Look for `.optional()` calls on the builder, or fields whose regex quantifier is `?` or `*`. Fields that are truly optional must use `.optional()` (e.g., `.number("(?:d)?,").optional()`) — NOT just `.number("(?:d),").optional()` which still requires the digit. A field like gps antenna state that should accept zero occurrences must use `(?:d)?` (zero or one digit) inside the `.number()` call, not `(?:d)` (exactly one digit).

- THEN the TG should write test cases that send messages **missing** the optional fields. For example, a GPS tracking command without the gps antenna state value should decode successfully without any exception, and the missing field should default to `null` or `0` in the resulting `Position` object.

- THEN the TG should verify that **no exception** (e.g., `IndexOutOfBoundsException`, `NumberFormatException`, `IllegalArgumentException`) is thrown when parsing a well-formed message that simply omits optional comma-separated fields.

- Common pitfall to avoid: Using `.number("(?:d),").optional()` when the intent is to allow zero occurrences of that digit. This syntax still requires a digit to be present; the `.optional()` only makes the entire group optional. To allow zero or one digit, the inside of the `.number()` must use `(?:d)?` (i.e., the `?` goes **inside** the number regex, not on the `.optional()` call). The correct version is `.number("(?:d)?,").optional()`.

- Example of a **correct** test (for the fixed decoder):
```java
// Sends a message missing the gps antenna state field (omitted entirely)
String sentence = "*HQ,123456789012345,V1,012345,,,,,,,,,0.0,0.0,0.0,0,0,0,0,0,0,0,0,,,0,0,0,0,20250101000000,80,1,2,3,4#";
Object result = decoder.decode(null, null, sentence);
assertNotNull(result);
assertTrue(result instanceof Position);
```

- Example of an **incorrect** test (that would pass on the buggy version but fail on the fixed):
```java
// Wrong: sends a message with gps antenna state present as "0" — doesn't test the optional absence
String sentence = "*HQ,123456789012345,V1,012345,,,,,,,,,0.0,0.0,0.0,0,0,0,0,0,0,0,0,,,0,0,0,0,20250101000000,80,1,2,0,3,4#";
Object result = decoder.decode(null, null, sentence);
assertNotNull(result);
```
This test never exercises the bug, because it includes the field. The bug only manifests when the field is absent.