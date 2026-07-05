---
name: regex-encoding-validation
description: WHEN validating iterator options that involve character encoding (e.g.,
  Charset.forName()), THEN test that an IllegalArgumentException is thrown for invalid
  encoding names. This skill applies to any OptionDescriber whose validateOptions
  method calls Charset.forName() on user-provided strings.
code_tags:
- BOUNDARY_CHECK
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# regex-encoding-validation

## Instructions

# Regex Encoding Validation

## Instructions

- WHEN the TG encounters an iterator class that accepts a character encoding option via `OptionDescriber` interface (e.g., `RegExFilter` with `ENCODING` option), and the `validateOptions(Map<String,String> options)` method calls `Charset.forName(options.get(ENCODING))` to validate the encoding string
- THEN the TG should write a test that:
  1. Creates an instance of the SkeletonIterator/iterator class
  2. Calls `validateOptions()` with a map containing an invalid encoding name (e.g., `"invalid_charset"` for the `ENCODING` key)
  3. Verifies that an `IllegalArgumentException` is thrown (because `Charset.forName()` throws `IllegalArgumentException` for unknown charset names)
  4. Also verify that the iterator works normally with a valid encoding (e.g., `"UTF-8"` or `"ISO-8859-1"`)

- Common pitfalls to avoid:
  - Testing only with valid encoding strings and never testing invalid ones
  - Asserting the wrong exception type — `Charset.forName()` throws `IllegalArgumentException`, not `UnsupportedCharsetException`
  - Not testing that the encoding option is actually consumed: ensure the test sets the option key that the code reads (e.g., look for the string constant like `RegExFilter.ENCODING` or the literal `"encoding"` in the options map)
  - Forgetting that an empty encoder map (no `ENCODING` key at all) should succeed (the code falls back to a default encoding)

## Examples

### Correct test (catches the bug):
```java
@Test
public void testInvalidEncoding() {
  RegExFilter filter = new RegExFilter();
  Map<String,String> options = new HashMap<>();
  options.put(RegExFilter.ENCODING, "invalid_charset_name");
  // This should throw IllegalArgumentException from Charset.forName()
  assertThrows(IllegalArgumentException.class, () -> filter.validateOptions(options));
}

@Test
public void testValidEncoding() {
  RegExFilter filter = new RegExFilter();
  Map<String,String> options = new HashMap<>();
  options.put(RegExFilter.ENCODING, "UTF-8");
  assertTrue(filter.validateOptions(options));
}
```

### Incorrect test (does not catch the bug):
```java
@Test
public void testOptions() {
  RegExFilter filter = new RegExFilter();
  Map<String,String> options = new HashMap<>();
  options.put("encoding", "UTF-8");  // OK but incomplete
  // Never tests with an invalid encoding value
  assertTrue(filter.validateOptions(options));
}
```