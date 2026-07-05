---
name: java-uri-multiarg-constructor-url-encoding
description: 'When testing URL encoding methods that use Java''s URI multi-argument
  constructor (new URI(scheme, userInfo, host, port, path, query, fragment)), verify
  the specific encoding behavior: non-ASCII characters are NOT encoded, already percent-encoded
  sequences ARE re-encoded (% becomes %25), brackets are encoded in path but NOT in
  query (sub-delimiters), and spaces are encoded in all components.'
code_tags:
- URL_ENCODING
- CHARACTER_ENCODING
- VALIDATION
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
  - URI multi-argument constructor
  - encodeUrl
  - toExternalForm
  - URL encoding
  - percent encoding
  - new URI(scheme
---

WHEN the TG encounters a method that encodes a URL by passing individual components to Java's new URI(scheme, userInfo, host, port, path, query, fragment), THEN test: (1) non-ASCII chars like ü pass through unencoded, (2) already percent-encoded sequences like %20 get double-encoded to %2520, (3) brackets [ ] are encoded in path (%5B %5D) but NOT in query, (4) spaces are encoded as %20 in all components, (5) the method is NOT idempotent due to % re-encoding. Use parametric tests covering each component separately.