---
name: version-comparison-ordering
description: When testing version comparison logic (compareTo), verify that version
  ordering is consistent and transitive. This skill helps catch bugs where versions
  with qualifiers (e.g., "1.0-rc1", "1.0-alpha") are misordered relative to each other
  or to plain numeric versions.
code_tags:
- ORDER_DEPENDENCY
test_pattern: PARAMETRIC_TEST
---

# version-comparison-ordering

## Instructions

# Version Comparison Ordering

## Instructions

- WHEN testing a class that implements `Comparable` (such as `ComparableVersion`) with a `compareTo(Item)` method that compares version items like `IntegerItem` and `StringItem`:
  - THEN test multiple version pairs in a pairwise comparison matrix, verifying transitivity (if A < B and B < C then A < C) and consistency (A < B implies B > A).
  - Include versions with qualifiers (e.g., `"1.0-alpha"`, `"1.0-rc1"`, `"1.0"`) and ensure that a qualifier version is always less than the same version without qualifier (e.g., `"1.0-rc1" < "1.0"`).
  - Include edge cases like empty qualifiers, numeric qualifiers, mixed-case qualifiers, and qualifiers that are purely numeric (e.g., `"1-1" < "1-2"`).
  - Test that the ordering of qualifiers follows Maven's convention: `alpha < beta < milestone < rc < snapshot < '' (no qualifier) < sp`.

- **Common pitfalls**:
  - Testing only plain numeric versions (e.g., "1.0" vs "2.0") and neglecting qualifier variants.
  - Assuming that compareTo is symmetric by testing only one direction (e.g., only assert `x < y` without also asserting `y > x`).
  - Overlooking the special ordering rule that a version with a qualifier (like "-rc1") is LESS than the same version without qualifier (like "1.0").
  - Not testing that qualifiers that are unrecognized should sort in alphabetical order after recognized qualifiers.

- **Example** (correct):
  ```java
  assertTrue("expected '1.0-rc1' < '1.0'", new ComparableVersion("1.0-rc1").compareTo(new ComparableVersion("1.0")) < 0);
  assertTrue("expected '1.0.0' > '1.0-rc1'", new ComparableVersion("1.0.0").compareTo(new ComparableVersion("1.0-rc1")) > 0);
  assertTrue("expected '1.0-alpha' < '1.0-rc1'", new ComparableVersion("1.0-alpha").compareTo(new ComparableVersion("1.0-rc1")) < 0);
  ```

- **Example** (incorrect — missing qualifier ordering test):
  ```java
  // Only testing numeric version ordering
  assertTrue(new ComparableVersion("1.0").compareTo(new ComparableVersion("2.0")) < 0);
  // Missing: qualifier versions like "1.0-rc1" compared with "1.0"
  ```