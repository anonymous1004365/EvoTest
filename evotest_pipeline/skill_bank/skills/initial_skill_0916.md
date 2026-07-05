---
name: path-normalization-in-getnodes
description: When testing methods that accept JCR path strings like getNodes(), always
  test that the method correctly normalizes paths — specifically that it strips trailing
  slashes from paths. Without normalization, passing "/" vs "" can produce different
  results like "[/]test" instead of "[test]".
code_tags:
- ARRAY_INDEX_ACCESS
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# path-normalization-in-getnodes

## Instructions

# Path Normalization for getNodes-like Methods

## Instructions

- WHEN the TG is testing a method that accepts a JCR path (like `DocumentMK.getNodes(String path, ...)`, `DocumentNodeStore.getNode(String path, ...)`, or similar methods that look up/retrieve nodes by path)
- THEN the TG should verify that trailing slashes in path strings are correctly normalized. Specifically:
  - A path like `"/"` should produce the same result as `""` (empty string) — both should be treated as the root path
  - A buggy implementation may return different results for `getNodes("/", ...)` vs `getNodes("", ...)`, where the root path with `"/"` incorrectly includes a leading slash in the output (e.g., output `"[/]test"` instead of `"[test]"`)
  - The test should invoke the method with both `"/"` and `""` as the path argument, and assert that the returned node state or identifier is equivalent
  - With `DocumentMK.getNodes()`, test that `getNodes("/", ...)` returns the same JSON structure as `getNodes("", ...)`, particularly that child node names in the JSON do NOT start with `"/"`

- Common pitfalls to avoid:
  - Testing only with `"/"` or only with `""` but not both
  - Assuming that path parsing inside the method handles trailing slashes correctly without explicit verification
  - Forgetting to check that child node names in the returned structure are properly normalized (no leading slash prefix on node names)

### Correct Example (would detect this bug)

```java
// Test that path "/" and "" produce equivalent results  
String rev = mk.getHeadRevision();
String resultWithSlash = mk.getNodes("/", rev, 0, 0, Integer.MAX_VALUE, null);
String resultWithoutSlash = mk.getNodes("", rev, 0, 0, Integer.MAX_VALUE, null);
// The failure in the buggy code was that getNodes("/", ...) returned 
// "[/]test" while getNodes("", ...) returned "[test]"
assertEquals(resultWithoutSlash, resultWithSlash);
```

### Incorrect Example (would NOT detect this bug)

```java
// Testing only with "/" — misses the normalization issue
String rev = mk.getHeadRevision();
String result = mk.getNodes("/", rev, 0, 0, Integer.MAX_VALUE, null);
// Only checks that the result is not null, but doesn't check
// that child names don't have a spurious leading "/"
assertNotNull(result);
```