---
name: string-split-regex-metacharacter-escaping
description: WHEN a method uses String.split(delimiter) where the delimiter is a user-provided
  or configurable string (e.g., a custom separator from setAllowMultipleValues), THEN
  test that regex metacharacters in the delimiter are treated as literal characters,
  not regex patterns. The fix typically involves Pattern.quote(delimiter).
code_tags:
- STRING_SPLIT
- REGEX_ESCAPE
- PATTERN_QUOTE
- CUSTOM_SEPARATOR
test_pattern: PARAMETRIC_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - PASS_BOTH
  - PASS_FAIL
  transition_tags: []
  keywords:
  - split
  - separator
  - delimiter
  - Pattern.quote
  - regex
  - metacharacter
  - custom separator
---

WHEN the TG encounters code that calls String.split(separator) where separator is a parameter, configuration value, or builder-set value, THEN: 1) Identify if the separator could contain regex metacharacters (., [, ], *, +, ?, ^, $, |, \, (, ), {, }). 2) Test with a separator that is a regex metacharacter (e.g., '.') and a value containing that character (e.g., '2.00.3.00'). 3) Verify the split treats the separator as a literal character, not a regex pattern. 4) If the code does NOT use Pattern.quote(), the test should fail on the buggy version and pass on the fixed version.