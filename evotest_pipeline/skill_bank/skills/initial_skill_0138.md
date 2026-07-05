---
name: url-validator-parentheses-test
description: When validating URL/URI patterns that use regex character classes like
  `\\(\\)`, test that parentheses and other special characters in URL paths are correctly
  accepted. The existing PATH_PATTERN explicitly includes escaped parentheses, so
  the validator should accept URLs with parentheses in the path component.
code_tags:
- REGEX_VALIDATION
- INPUT_VALIDATION
test_pattern: PARAMETRIC_TEST
---

# url-validator-parentheses-test

## Instructions

# URL Validator Parentheses in Paths

## Instructions

- WHEN the code uses a URL validator that validates URLs against a regex pattern (e.g., `PATH_PATTERN = "^(/[-\\w:@&?=+,.!/~*'%$_;\\(\\)]*)?$"`) which explicitly includes escaped parentheses `\\(` and `\\)` in its allowed character set:
  - THEN write parametrized test cases that supply valid URLs containing parentheses in the path, such as:
    - `http://example.com/path(with)parens`
    - `http://example.com/file(1).html`
    - `http://example.com/(group)/resource`
    - `http://example.com/path/with/(nested/parentheses)/test`
  - THEN verify that `validator.isValid(url)` returns `true` for these URLs.
  - THEN verify that `validator.isValid(url)` returns `false` for truly invalid URLs (e.g., malformed schemes, missing host) to confirm validation logic is not completely disabled.

- WHEN a test fails on URL validation with parentheses:
  - THEN check the regex pattern definition carefully — if the pattern includes `\\(\\)` (escaped parentheses), the intent is to allow them.
  - THEN inspect the `isValid` method to ensure the regex pattern is being compiled and applied correctly and the path component is properly extracted before matching.
  - THEN verify the path extraction logic (e.g., how the URL is parsed into scheme, authority, path components) does not strip or reject parentheses before the regex match.

- Common pitfalls to avoid:
  - DO NOT test only URLs without special characters — parentheses are a common edge case that regex patterns easily break on.
  - DO NOT assume that because a regex looks permissive, it actually works — compile and run a concrete test against the actual validator.
  - DO NOT test the regex in isolation (e.g., `Pattern.compile(PATH_PATTERN).matcher(path).matches()`) — test through the full `UrlValidator.isValid()` pipeline to exercise URL parsing, component extraction, and validation.
  - DO NOT forget to test negative cases (invalid URLs still rejected) when investigating a bug — to ensure the fix doesn't simply disable validation.

- Correct test example:
```java
// Tests that URLs with parentheses in the path are valid
String[] validUrls = {
    "http://example.com/path(with)parens",
    "http://example.com/file(1).html",
    "http://example.com/(group)/resource"
};
UrlValidator validator = new UrlValidator();
for (String url : validUrls) {
    assertTrue("URL should be valid: " + url, validator.isValid(url));
}
```

- Incorrect test example (fails to detect the bug):
```java
// Only tests URLs without special characters
String[] validUrls = {
    "http://example.com/path",
    "http://example.com/file.html",
    "http://example.com/group/resource"
};
UrlValidator validator = new UrlValidator();
for (String url : validUrls) {
    assertTrue("URL should be valid: " + url, validator.isValid(url));
}
// This passes even on the buggy version, missing the parentheses issue entirely.
```