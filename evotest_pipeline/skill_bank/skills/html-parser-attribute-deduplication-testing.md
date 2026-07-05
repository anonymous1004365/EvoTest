---
name: html-parser-attribute-deduplication-testing
description: When testing HTML parser attribute deduplication, verify that duplicate
  attributes are correctly removed (first value kept), error reporting is 1 error
  per element with duplicates, Element.attr() is case-insensitive (use attributes().get(key)
  for case-sensitive access), XML parsers do not report dedup errors, and ParseSettings.preserveCase
  treats different-case attributes as distinct.
code_tags:
- VALIDATION
- STATE_MUTATION
- HTML_PARSING
- ATTRIBUTE_DEDUPLICATION
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - PASS_FAIL
  - BUG_DETECTED
  transition_tags: []
  keywords:
  - jsoup
  - attribute deduplication
  - HTML parser
  - parseInput
  - duplicate attributes
  - HtmlTreeBuilder
  - dedupeAttributes
---

WHEN testing HTML parser attribute deduplication: 1) Use Parser.htmlParser().setTrackErrors(N) to capture errors. 2) Verify first attribute value is kept (e.g., '<img src=foo SRC=bar>' keeps 'foo'). 3) Error count is 1 per element with duplicates, not 1 per duplicate pair. 4) Element.attr(key) is case-insensitive; use element.attributes().get(key) for case-sensitive access. 5) XML parser (Parser.xmlParser()) does NOT report dedup errors. 6) ParseSettings.preserveCase treats different-case attributes as distinct (not duplicates). 7) Test void elements (img, br, hr, input, link, meta) and normal elements.