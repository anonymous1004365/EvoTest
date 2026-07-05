---
name: uri-parameter-duplicate-preservation
description: When normalizing URIs with duplicate query parameters, the normalized
  output must preserve all duplicate values. The TG should test URI normalization
  functions with duplicate parameter keys to ensure values are not lost during normalization.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# uri-parameter-duplicate-preservation

## Instructions

# URI Normalization with Duplicate Parameters

## Instructions

- WHEN the TG encounters a `normalizeUri(String uri)` method (such as `URISupport.normalizeUri`) that reorders query parameters alphabetically, or any URI normalization that calls `parseQuery` followed by `createQueryString`:

  - THEN the TG should test with URIs containing **duplicate parameter keys** (same key appearing multiple times with different values). 
  - The test must verify that ALL values for duplicate keys are preserved in the normalized output, not just the last value.
  - For example: `"smtp://localhost?to=foo&to=bar&from=me"` should produce `"smtp://localhost?from=me&to=foo&to=bar"` — note both `to=foo` and `to=bar` appear, and parameters are sorted alphabetically by key.
  - The TG should test with at least 2 duplicate keys (e.g., `to` appearing twice and `from` appearing twice).
  - The TG should verify the ordering: parameters with the same key must appear in the **original insertion order** after normalization.
  - Use `assertEquals` to compare the normalized output against the expected string. On the buggy version (before the fix), duplicate parameter values will be lost — only the last value for each duplicate key will survive.

- Common pitfalls to avoid:
  - ❌ Testing only with unique parameter keys — this does not expose the bug
  - ❌ Assuming the normalized output preserves the original parameter order verbatim — parameters are reordered alphabetically by key name
  - ❌ Testing only a single duplicate key in isolation — test with two different duplicate keys to ensure the fix handles the general case
  - ❌ Verifying only the count of occurrences — use exact string matching on the full normalized URI

### Correct Example
```java
public void testNormalizeEndpointUriWithDualParameters() throws Exception {
    String out1 = URISupport.normalizeUri("smtp://localhost?to=foo&to=bar&from=me");
    assertEquals("smtp://localhost?from=me&to=foo&to=bar", out1);

    String out2 = URISupport.normalizeUri("smtp://localhost?to=foo&to=bar&from=me&from=you");
    assertEquals("smtp://localhost?from=me&from=you&to=foo&to=bar", out2);
}
```

### Incorrect Example
```java
// WRONG: only tests unique keys — will not catch duplicate parameter loss
public void testNormalizeEndpointUri() throws Exception {
    String out1 = URISupport.normalizeUri("smtp://localhost?username=davsclaus&password=secret");
    String out2 = URISupport.normalizeUri("smtp://localhost?password=secret&username=davsclaus");
    assertEquals(out1, out2);
}
```