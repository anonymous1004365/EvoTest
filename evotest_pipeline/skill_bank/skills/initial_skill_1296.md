---
name: jcr-path-whitespace-validation
description: When testing JCR name/path resolution code that handles JCR names with
  leading/trailing whitespace, ensure that such names are properly resolved using
  local namespace mappings rather than returning null. The TG should test JCR names
  with whitespace to verify they are not silently rejected.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# jcr-path-whitespace-validation

## Instructions

# JCR Path Whitespace Validation

## Instructions

- WHEN the TG encounters code that resolves JCR paths or names (e.g., `getJCRPath`, `getOakPath`, `JcrPath`, `NameMapper`, `NamePathMapper`) that handles namespace-prefixed JCR names like `"jcr:content"` or `"oak:leading"` where whitespace (leading, trailing, or embedded spaces) may be present in the local part of the qualified name
- THEN the TG should write a test method that:
  1. Creates a JCR path/name string that includes leading whitespace in the local part (e.g., `"oak: leading"` has a space after the colon)
  2. Passes this path through the name/path resolution method (e.g., `getJCRPath`, `getOakPath`, or the name mapper's resolution method)
  3. Asserts that the resolved value is NOT null — the whitespace-containing local name should be preserved in the output, not discarded
  4. The test should use both short names (e.g., `"oak: leading"`) and full paths (e.g., `"/oak: leading/path"`)

- Common pitfalls to avoid:
  - **Only testing valid/clean namespace-prefixed names** — The TG might assume that all JCR names follow strict patterns without whitespace
  - **Not testing the local part** — The TG might test namespace prefix handling but forget to verify that the local name (the part after the colon) correctly preserves whitespace
  - **Testing only the session-level API** — The bug is in the lower-level name path mapper, so tests should target that class directly

### Example (Correct)
```java
@Test
public void testJcrNameWithLeadingSpaceInLocalPart() {
    NamePathMapperImpl mapper = new NamePathMapperImpl(/* with registered local mappings */);
    // "oak: leading" has a space after the colon in the local part
    String result = mapper.getJCRPath("oak: leading");
    assertNotNull("JCR name with whitespace should not be null", result);
    assertEquals("oak: leading", result);
}
```

### Example (Incorrect)
```java
@Test
public void testJcrNameOnlyClean() {
    NamePathMapperImpl mapper = new NamePathMapperImpl(/* with registered local mappings */);
    // Only tests clean names without whitespace — misses the whitespace bug
    assertEquals("oak:leading", mapper.getJCRPath("oak:leading"));
}
```