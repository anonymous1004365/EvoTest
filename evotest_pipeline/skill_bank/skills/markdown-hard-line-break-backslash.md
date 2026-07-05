---
name: markdown-hard-line-break-backslash
description: When testing a markdown parser that supports hard line breaks via backslash
  at end of line (CommonMark spec), verify that a backslash immediately before a newline
  produces a <br> tag. The bug typically manifests as a regex change in the INLINE_BR
  pattern from ^ {2,}\n(?!\s*$) to ^( {2,}|\\)\n(?!\s*$).
code_tags:
- MARKDOWN_PARSING
- HARD_LINE_BREAK
- COMMONMARK
- INLINE_REGEX
- REGEX_PATTERN_CHARACTER_MISMATCH
test_pattern: PARAMETRIC_TEST
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
  - markdown
  - hard line break
  - backslash
  - CommonMark
  - INLINE_BR
  - regex
  - markedj
---

WHEN the TG encounters a markdown parser where the INLINE_BR regex is modified to add backslash support: THEN test (1) backslash at EOL produces <br>, (2) multiple consecutive backslash line breaks each produce <br>, (3) backslash followed by blank line does NOT produce <br> (paragraph break takes precedence), (4) the breaks option interacts correctly. Use input like 'Line 1\\\nLine 2' and expect '<p>Line 1<br>\n Line 2</p>'. Common pitfall: testing only 2+ spaces before newline (the old behavior) and missing the backslash case.