---
name: newest-revision-truncation-inequality
description: Use this skill when testing methods that compute the "newest" revision
  among multiple candidates by comparing timestamps or revision vectors. The TG should
  verify that the comparison correctly handles equal timestamps by falling through
  to cluster node IDs, instead of truncating the revision value early.
code_tags:
- REVISION_TRACKING_NEWEST
test_pattern: PARAMETRIC_TEST
---

# newest-revision-truncation-inequality

## Instructions

# Newest Revision Truncation Inequality

## Instructions

- WHEN the TG encounters a method that finds the "newest" revision among multiple revision candidates by comparing their timestamps and/or cluster node IDs (e.g., `getNewestRevision` in `NodeDocument.java`)
- THEN the TG should test that **when two revisions have the same timestamp** (i.e., `Revision.compareRevisionTime` returns 0 or `getTimestamp()` returns equal values), the method **does not truncate/return the comparison result early** but instead falls through to compare by **cluster node ID** to determine which revision is genuinely newer
- Specifically, the TG should construct test cases with:
  - Two `Revision` objects that share the **same timestamp** but have **different cluster node IDs** (e.g., `Revision(12345, 0, 1)` and `Revision(12345, 0, 2)` where `12345` is the same timestamp)
  - Verify that the method returns the revision with the **higher cluster node ID** (the newer one), not truncating early because the timestamps compared equal
- Also test the case where **only one revision exists** at the exact timestamp to ensure correct candidate filtering
- Common pitfalls to avoid:
  - Testing only revisions with **different timestamps** — this does not exercise the truncation bug
  - Testing only **single-revision scenarios** where no comparison happens
  - Assuming that equal timestamps means the revisions are interchangeable — they are not; different cluster node IDs make one newer than the other
  - Writing tests that pass on the buggy version because they assert the wrong (truncated) revision

### Example (correct test pattern)

```java
// Covers the truncation bug: two revisions with same timestamp but different cluster node IDs
Revision r1 = new Revision(12345, 0, 1); // timestamp=12345, counter=0, clusterId=1
Revision r2 = new Revision(12345, 0, 2); // timestamp=12345, counter=0, clusterId=2

// r2 should be "newer" because same timestamp but higher cluster node ID
// Buggy version might truncate and return r1 (or wrong revision)
Revision newest = doc.getNewestRevision(context, new RevisionVector(baseRev),
    Sets.newHashSet(r1, r2), changeRev, path);
assertEquals("Newest revision with same timestamp should pick higher clusterId", r2, newest);
```

### Example (incorrect test pattern — does NOT catch the bug)

```java
// INCORRECT: Revisions have different timestamps, so comparison never hits the truncation case
Revision r1 = new Revision(10000, 0, 1);
Revision r2 = new Revision(20000, 0, 2);

// This would pass on both buggy and fixed versions — no value
Revision newest = doc.getNewestRevision(context, new RevisionVector(baseRev),
    Sets.newHashSet(r1, r2), changeRev, path);
assertEquals(r2, newest);
```