---
name: locale-extraction-from-filename-without-separator
description: WHEN testing methods that extract locale/prefix from filenames using
  separator-based parsing (e.g., Strings.lastPathComponent), THEN test with filenames
  that contain no separator character to verify graceful handling. This skill prevents
  bugs where methods fail on filenames without the expected separator.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# locale-extraction-from-filename-without-separator

## Instructions

# Locale Extraction from Filename Without Separator

## Instructions

WHEN testing a method that parses a filename to extract a locale, prefix, or sub-component by looking for a separator character (e.g., dot '.', underscore '_', slash '/'):

- THEN include a test case where the input filename DOES NOT CONTAIN the separator character at all (e.g., `"some.ext"` when the method looks for a suffix like locale after a dot separator).
- THEN verify that the output path (the filename portion) remains unchanged — the method should NOT strip or modify the filename when no separator is found.
- THEN verify that the extracted locale or sub-component is null/empty when no separator is present in the filename.
- THEN also test with a filename that DOES contain the separator followed by the expected component (e.g., `"some_en.ext"`) to verify the normal extraction path works as a control.

**Common pitfalls to avoid:**
- Testing only with filenames that contain the separator — this misses the bug where the method incorrectly strips content when no separator exists.
- Assuming `Strings.lastPathComponent()` or similar utility methods always return the portion after the separator — check what they return when the separator is absent from the input.
- Not testing the "path" field of the result object separately from the "locale" field — both fields may be affected by the same parsing logic.

**Correct test pattern:**
```java
// Test filename WITHOUT separator
PathLocale result = ResourceUtils.getLocaleFromFilename("some.ext");
assertThat("Path should remain unchanged", result.path, is(equalTo("some.ext")));
assertNull("Locale should be null when no locale suffix", result.locale);

// Test filename WITH separator (control)
PathLocale result2 = ResourceUtils.getLocaleFromFilename("some_en.ext");
assertThat("Path should strip the locale part", result2.path, is(equalTo("some.ext")));
assertThat("Locale should be extracted", result2.locale, is(equalTo(Locale.ENGLISH)));
```

**Incorrect test that misses the bug:**
```java
// Only testing with separator present — won't catch the bug
PathLocale result = ResourceUtils.getLocaleFromFilename("some_en.ext");
assertThat(result.path, is(equalTo("some.ext")));
assertThat(result.locale, is(equalTo(Locale.ENGLISH)));
// Missing: test with "some.ext" to verify path stays "some.ext"
```