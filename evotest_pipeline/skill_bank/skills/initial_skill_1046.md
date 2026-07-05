---
name: null-input-to-string-split
description: When a method takes a comma-separated String parameter that is parsed
  with Strings.split() and may be null, the TG should test that null is handled safely.
  Strings.split(null, ',') may throw a NullPointerException, so the constructor must
  guard against null before calling the split method.
code_tags:
- VALIDATION
- NULL_CHECK
- STRING_PARSING
test_pattern: EXCEPTION_TEST
---

# null-input-to-string-split

## Instructions

# Null Input to String Split Parsing

## Instructions

- WHEN the TG encounters a constructor or method that accepts a nullable String parameter and parses it using `Strings.split(theString, ',')` (or any char delimiter), AND the resulting array is used for iteration/comparison later.
- THEN the TG should write a test that passes `null` as that String parameter and verifies that the method does not throw a `NullPointerException`.
- Include a test case that calls the method with `null` explicitly (e.g., `someMethod(null)`) and asserts that either `false` is returned (for a boolean method) or no exception is thrown.
- **Common pitfall**: Writing tests that only pass empty string `""` or normal non-null strings but never null. The `Strings.split(s, c)` method throws `NullPointerException` when `s` is null (it delegates to `String.split()` internally). Any code path that calls `Strings.split()` with a parameter that can be null MUST be tested with null input.
- **Example (correct)** for the `UserAgent` enum (whose constructor accepts a nullable `notAllowed` String):
  ```java
  // UserAgent enum constructor calls Strings.split(notAllowed, ',') where notAllowed may be null
  // The constructor UserAgent(List<String>... detectionStrings) delegates to this(null, detectionStrings)
  // so the two-arg constructor must handle null notAllowed gracefully.
  // Test: INTERNET_EXPLORER.matches(null) should return false without NPE
  assertFalse(UserAgent.INTERNET_EXPLORER.matches(null));
  ```
- **Example (incorrect)** — only testing normal inputs:
  ```java
  // This only tests non-null inputs and misses the null case:
  assertTrue(UserAgent.INTERNET_EXPLORER.matches("Mozilla MSIE Trident"));
  // Missing: assertFalse(UserAgent.INTERNET_EXPLORER.matches(null));
  ```