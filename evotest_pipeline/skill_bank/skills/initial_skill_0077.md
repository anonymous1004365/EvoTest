---
name: jdk-version-range-inclusive-boundary
description: When testing JDK version range parsing with inclusive bounds ([1.5,1.6]),
  test version strings with underscores and build suffixes like "1.6.0_09-b03" to
  catch bugs in token normalization, especially the regex stripping of non-digit characters
  and the split on hyphen/underscore.
code_tags:
- VERSION_RANGE_PARSING
test_pattern: PARAMETRIC_TEST
---

# jdk-version-range-inclusive-boundary

## Instructions

# JDK Version Range Inclusive Boundary Testing

## Instructions

- WHEN the TG encounters code that parses JDK version range expressions like `[1.5,1.6]` or `(1.3,1.6)` and compares version strings dot-by-dot using tokenization logic
- THEN the TG should test with version strings that include underscore-separated build numbers (e.g., `"1.6.0_09"`, `"1.6.0_09-b03"`) AND also test the same versions without underscores (e.g., `"1.6"`, `"1.6.0"`) to verify that inclusive boundary checks work correctly across different version formats
- The TG should verify the profile IS activated when the `java.version` matches the upper bound exactly (e.g., `[1.5,1.6]` should activate for `"1.6"`, `"1.6.0"`, `"1.6.0_09"`, `"1.6.0_09-b03"`) and is NOT activated when the version is just below the lower bound (e.g., `"1.4"`, `"1.4.2"`, `"1.4.2_09"`, `"1.4.2_09-b03"`)
- Common pitfalls:
  - **Testing only simple version strings** like `"1.5"` and `"1.6"` without testing underscore/hyphen variants — the bug is in how `getRelationOrder()` strips non-numeric characters with `replaceAll("[^0-9\\.\\-\\_]", "")` and splits on `[\\.\\-\\_]`, which can cause tokenization mismatches between the range value (e.g., "1.6") and the actual version (e.g., "1.6.0_09")
  - **Only testing exclusive bounds** `(1.3,1.6)` without testing inclusive bounds `[1.5,1.6]` — the inclusive boundary case where `leftRelation == 0` triggers a short-circuit `return true` in `isInRange()`, which may mask tokenization bugs that appear at the boundary
  - **Failing to test both** the "edge just below" AND "edge exactly at" boundary scenarios with all version suffix formats

### Correct test pattern (catches the bug):
```java
Profile profile = newProfile("[1.5,1.6]");
// Should NOT activate below the range
assertActivation(false, profile, newContext(null, newProperties("1.4")));
assertActivation(false, profile, newContext(null, newProperties("1.4.2")));
assertActivation(false, profile, newContext(null, newProperties("1.4.2_09")));
assertActivation(false, profile, newContext(null, newProperties("1.4.2_09-b03")));
// Should activate at lower bound
assertActivation(true, profile, newContext(null, newProperties("1.5")));
assertActivation(true, profile, newContext(null, newProperties("1.5.0")));
assertActivation(true, profile, newContext(null, newProperties("1.5.0_09")));
assertActivation(true, profile, newContext(null, newProperties("1.5.0_09-b03")));
// Should activate at upper bound (inclusive)
assertActivation(true, profile, newContext(null, newProperties("1.6")));
assertActivation(true, profile, newContext(null, newProperties("1.6.0")));
assertActivation(true, profile, newContext(null, newProperties("1.6.0_09")));
assertActivation(true, profile, newContext(null, newProperties("1.6.0_09-b03")));
```

### Incorrect test pattern (misses the bug):
```java
Profile profile = newProfile("[1.5,1.6]");
assertActivation(false, profile, newContext(null, newProperties("1.4")));
assertActivation(true, profile, newContext(null, newProperties("1.5")));
assertActivation(true, profile, newContext(null, newProperties("1.6")));
// Missing: no "1.6.0", no "1.6.0_09", no "1.6.0_09-b03" variants
```