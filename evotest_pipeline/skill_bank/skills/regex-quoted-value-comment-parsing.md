---
name: regex-quoted-value-comment-parsing
description: 'When a config file parser (.env, .properties, .ini) uses a regex pattern
  with a negated character class like [^#]* to capture values, and the format supports
  quoted values (single or double quotes), test that values containing comment delimiters
  (like #) inside quotes are correctly preserved.'
code_tags:
- REGEX_PATTERN
- QUOTED_VALUE_PARSING
- CONFIG_PARSING
- COMMENT_PARSING
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - BUG_DETECTED
  - PASS_BOTH
  transition_tags: []
  keywords:
  - regex
  - quoted value
  - comment delimiter
  - config parser
  - dotenv
  - properties
  - negated character class
---

WHEN the TG encounters a config file parser that uses a regex with a negated character class like [^#]* to capture values, AND the format supports quoted values: THEN write a test with a quoted value containing a comment delimiter (e.g., KEY="value#with#hash") and assert the full value including the delimiter is returned. The bug is that the regex truncates at the delimiter even inside quotes. Test both single and double quotes if supported. Common pitfall: testing only unquoted values with delimiters (which should be truncated) — the bug is specifically about quoted values.