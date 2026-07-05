---
name: xml-block-tokenization-regex-atomic-group
description: When testing XML block tokenization using regex patterns with negative
  lookahead/lookbehind, ensure the regex uses an atomic group around the closing tag
  pattern to prevent catastrophic backtracking when element names are similar. The
  TG should test with sibling elements that have names starting with the same prefix
  as the target element name.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# xml-block-tokenization-regex-atomic-group

## Instructions

# XML Block Tokenization Regex Atomic Group

## Instructions

- WHEN the TG encounters XML block tokenization code that uses a regex with a negative lookahead pattern like `(?:(?!</{0}).)*</{0}\\s*>` to match XML element blocks (where `{0}` is a tag name substituted via `MessageFormat.format` or similar)
- THEN the TG should verify that the regex uses an atomic group `(?:(?!(</{0}\\s*>)).)*` instead of a regular non-capturing group `(?:(?!</{0}).)*`, because without an atomic group the regex can backtrack catastrophically when sibling element names are similar to the target element name
- Specifically, WHEN the tag token is a name like `"Trip"` and the parent token is `"Trips"`, THEN the regex pattern `<{0}(\\s+[^>]*)?>(?:(?!</{0}).)*</{0}\\s*>` would incorrectly match across sibling elements because `</Trip` could match `</Trips` and continue, whereas an atomic group around the closing tag pattern prevents backtracking and correctly matches only the intended element
- The TG should write a test that uses `tokenizeXML("Trip", "Trips")` or similar with XML content containing sibling elements whose names share a prefix with the target element (e.g., `<Trips><Trip>...</Trip><Trip>...</Trip></Trips>`), and verify that exactly the expected number of tokens is returned (e.g., 2 for two Trip elements), not fewer due to incorrect regex matching
- The test should assert that the size of the returned list of tokens matches the expected count and that each token is correctly bounded by the start and end tags
- Common pitfall: Testing only with completely distinct element names (e.g., `<person>` inside `<persons>`) which would work with either regex variant, missing the edge case where sibling element names share a prefix with the target element (e.g., `<Trip>` inside `<Trips>` with a sibling like `<Triple>`)

### Correct Example

```java
public void testTokenizeXMLPairWithSimilarChildNames() throws Exception {
    Expression exp = TokenizeLanguage.tokenizeXML("Trip", "Trips");
    exchange.getIn().setBody("<?xml version='1.0' encoding='UTF-8'?>"
        + "<Trips>"
        + "<Trip>Trip A</Trip>"
        + "<Trip>Trip B</Trip>"
        + "</Trips>");
    List<?> trips = exp.evaluate(exchange, List.class);
    assertEquals(2, trips.size());
    assertEquals("<Trip>Trip A</Trip>", trips.get(0));
    assertEquals("<Trip>Trip B</Trip>", trips.get(1));
}
```

### Incorrect Example (misses the edge case)

```java
public void testTokenizeXMLPair() throws Exception {
    Expression exp = TokenizeLanguage.tokenizeXML("<person>", null);
    exchange.getIn().setBody("<persons><person>James</person><person>Claus</person></persons>");
    List<?> names = exp.evaluate(exchange, List.class);
    assertEquals(2, names.size());
    // This test passes even with buggy regex because "person" and "persons" don't share
    // a closing tag prefix issue - the negative lookahead works fine here.
}
```