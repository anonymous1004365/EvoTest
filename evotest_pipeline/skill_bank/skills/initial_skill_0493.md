---
name: url-resolution-trailing-empty-segment
description: When resolving a relative URL against a base URL that has a trailing
  empty segment (e.g., Home/), the resolved URL should preserve the trailing slash.
  Test relative URL resolution against base URLs with empty trailing segments and
  verify the resulting URL string matches expected output.
code_tags:
- URL_PARSING
- STRING_MANIPULATION
test_pattern: STATE_TEST
---

# url-resolution-trailing-empty-segment

## Instructions

# URL Resolution: Trailing Empty Segment in Base URL

## Instructions

- **WHEN** the TG encounters a URL resolution method like `Url.resolveRelative(Url relative)` that resolves a relative URL against a base URL
- **THEN** the TG should write tests where the base URL has a trailing empty segment (e.g., `Url.parse("Home/")` which produces segments `["Home", ""]`) and test that:
  - Calling `resolveRelative` with a relative URL (e.g., `Url.parse("?0-1.ILinkListener-link")`) produces a result whose string representation includes the trailing slash from the base URL
  - The expected behavior is that the trailing slash is preserved in the resolved URL (e.g., `Home/?0-1.ILinkListener-link`), NOT stripped (e.g., `Home?0-1.ILinkListener-link`)
  - Use `assertEquals` with the expected string and `url.toString()` or `url.toString(StringMode.LOCAL)`

- **WHEN** the TG encounters any URL resolution involving base URLs parsed from strings like `"Home/"`, `"foo/"`, `"bar//"`, or any URL whose `getSegments()` last element is `""`
- **THEN** the TG should test that the trailing empty segment is preserved after resolution, by comparing the full string output of the resolved URL against the expected string that includes the trailing slash

- **Common pitfalls to avoid:**
  - ❌ Testing only the segment list after resolution without checking the string representation — the empty trailing segment might be in the list but the `toString()` method might not render it as a trailing slash
  - ❌ Assuming that query parameters attached to the relative URL (e.g., `?0-1.ILinkListener-link`) don't interact with the trailing slash preservation logic
  - ❌ Testing only base URLs without empty trailing segments — the bug only manifests when the base URL has an empty trailing segment AND the relative URL has only query parameters (no path segments)

- **Example correct approach:**
  ```java
  Url baseUrl = Url.parse("Home/");
  Url relative = Url.parse("?0-1.ILinkListener-link");
  baseUrl.resolveRelative(relative);
  assertEquals("Home/?0-1.ILinkListener-link", baseUrl.toString());
  ```

- **Example incorrect approach (buggy version):**
  ```java
  Url baseUrl = Url.parse("Home/");
  Url relative = Url.parse("?0-1.ILinkListener-link");
  baseUrl.resolveRelative(relative);
  // BUG: actual result is "Home?0-1.ILinkListener-link" — trailing slash is lost!
  assertEquals("Home/?0-1.ILinkListener-link", baseUrl.toString());
  ```