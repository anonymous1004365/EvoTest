---
name: release-range-bounds-reject-snapshots
description: WHEN validating version range bounds intended for release artifacts,
  THEN test that range bounds containing SNAPSHOT versions are properly rejected or
  restricted. This skill helps catch missing validation of snapshot versions within
  release version ranges.
code_tags:
- SNAPSHOT_VERSION_RANGE_VALIDATION
- VALIDATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# release-range-bounds-reject-snapshots

## Instructions

# Release Range Bounds Must Not Contain Snapshot Versions

## Instructions

- WHEN the TG encounters a version range parsing method (e.g., `VersionRange.createFromVersionSpec(String)`) that creates range constraints from string specifications like `[1.0,2.0)` or `[1.0,)`
- THEN it should test that version ranges created with the explicit intent of representing a "release" range do not silently accept snapshot versions (`SNAPSHOT`) within their bounds, and instead throw an appropriate exception or fail validation
- Specifically: Test that when `createFromVersionSpec` processes a range string like `[1.0-SNAPSHOT,2.0)`, `[1.0,2.0-SNAPSHOT)`, or `[1.0-SNAPSHOT,2.0-SNAPSHOT]` — where one or both bounds contain the literal string `SNAPSHOT` — the method throws an `InvalidVersionSpecificationException`
- The test should verify the exception message contains relevant context about rejecting snapshots in release range bounds
- **Common pitfalls**:
  - Testing only valid ranges and ignoring invalid ones that mix snapshot versions in range bounds
  - Assuming the validation is done at the version level rather than checking it at the range boundary level
  - Forgetting to test edge cases like: only one bound has a snapshot, both bounds have snapshots, and snapshots in unbounded ranges like `[1.0-SNAPSHOT,)`
  - Testing snapshot rejection for single versions (e.g., `1.0-SNAPSHOT` without range brackets) — single version specs should still parse normally; only range bounds with brackets/parens are the concern

- **Correct example**:
  ```java
  @Test
  public void testReleaseRangeBoundsCannotContainSnapshots() {
      assertThrows(InvalidVersionSpecificationException.class,
          () -> VersionRange.createFromVersionSpec("[1.0-SNAPSHOT,2.0)"),
          "Range bound containing SNAPSHOT should be rejected");
      
      assertThrows(InvalidVersionSpecificationException.class,
          () -> VersionRange.createFromVersionSpec("[1.0,2.0-SNAPSHOT)"),
          "Range bound containing SNAPSHOT should be rejected");
      
      assertThrows(InvalidVersionSpecificationException.class,
          () -> VersionRange.createFromVersionSpec("[1.0-SNAPSHOT,2.0-SNAPSHOT]"),
          "Range bound containing SNAPSHOT should be rejected");
  }
  ```

- **Incorrect example** (too narrow — only checks one case, misses edge cases):
  ```java
  @Test
  public void testReleaseRangeBoundsCannotContainSnapshots() {
      // Only testing one bound with SNAPSHOT — incomplete coverage
      assertThrows(InvalidVersionSpecificationException.class,
          () -> VersionRange.createFromVersionSpec("[1.0-SNAPSHOT,2.0)"));
  }
  ```