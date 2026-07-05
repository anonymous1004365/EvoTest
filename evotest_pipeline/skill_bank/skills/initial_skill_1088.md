---
name: locale-extraction-from-filename
description: When testing methods that extract locale from filenames using regex patterns,
  ensure the test covers edge cases where the regex may partially match but the matched
  segments fail ISO validation, causing the method to return unexpected results like
  ArrayIndexOutOfBoundsException. Also test filenames without any locale pattern to
  verify they return null locale correctly.
code_tags:
- EXCEPTION_HANDLING
- LOCALE_EXTRACTION_FROM_FILENAME
test_pattern: PARAMETRIC_TEST
---

# locale-extraction-from-filename

## Instructions

# Locale Extraction from Filename with Regex Pattern

## Instructions

WHEN the TG encounters a method that uses a regex pattern to extract locale information (language, country, variant) from filenames — specifically where the regex groups capture `_([a-z]{2})(_([A-Z]{2})(_([^_\\.]+))?)?(\\.min)?$` — and validates captured groups against ISO language/country sets (`isoLanguages`, `isoCountries`):

- THEN the TG MUST write a test that passes a filename where the regex matches but the captured language string does NOT exist in `isoLanguages`. For example, using `ResourceUtils.getLocaleFromFilename("some.xx_YY.ext")` where `"xx"` is not a valid ISO language code. The test should verify that the method gracefully handles this case and returns a `PathLocale` with `locale == null` and `path` equal to the original filename, WITHOUT throwing any exception.

- THEN the TG MUST also test filenames that contain a locale that IS in the ISO sets (`"some.en_US.ext"` should return `Locale.US`), filenames with `.min` postfix (`"some.min.ext"` should return null locale), and filenames without any locale at all (`"some.ext"` should return null locale).

- Common pitfalls to avoid:
  - Testing only with valid ISO language codes (e.g., `en`, `fr`, `de`) while ignoring invalid codes that still match the regex pattern (e.g., `xx`, `yy`, `zz`).
  - Forgetting to test filenames that lack any locale pattern at all (e.g., `"some.ext"`), which should produce a `null` locale.
  - Forgetting to test `.min` prefixed filenames that don't have a locale (e.g., `"some.min.ext"`), which should also produce a `null` locale.

### Correct Example (should pass on both buggy and fixed versions)

```java
// Test filename with no locale at all
PathLocale pl = ResourceUtils.getLocaleFromFilename("some.ext");
assertThat(pl.path, is(equalTo("some.ext")));
assertThat(pl.locale, is(nullValue()));

// Test filename with .min but no locale
pl = ResourceUtils.getLocaleFromFilename("some.min.ext");
assertThat(pl.path, is(equalTo("some.min.ext")));
assertThat(pl.locale, is(nullValue()));

// Test filename with valid locale
pl = ResourceUtils.getLocaleFromFilename("some.en_US.min.ext");
assertThat(pl.path, is(equalTo("some.min.ext")));
assertThat(pl.locale, is(Locale.US));

// Test filename with invalid ISO language code (matches regex but not in isoLanguages)
pl = ResourceUtils.getLocaleFromFilename("some.xx_YY.ext");
assertThat(pl.path, is(equalTo("some.xx_YY.ext")));
assertThat(pl.locale, is(nullValue()));
```

### Incorrect Example (only tests valid locales, misses edge cases)

```java
// WRONG: Only tests valid international locale
PathLocale pl = ResourceUtils.getLocaleFromFilename("some.en_US.min.ext");
assertThat(pl.locale, is(Locale.US));

// Missing: test for filenames without locale
// Missing: test for filenames with .min but no locale  
// Missing: test for filenames with invalid ISO language code
```