---
name: empty-branch-commit-returns-head-revision
description: When a MicroKernel implementation's commit method handles empty commits
  (no changes), the test must verify that an empty branch commit returns the current
  head revision of that branch, not the base revision. Use this skill when testing
  branch commit operations where the payload is empty.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# empty-branch-commit-returns-head-revision

## Instructions

# Empty Branch Commit Returns Head Revision

## Instructions

- WHEN the TG encounters a MicroKernel (or similar revision-based system) `commit` method that receives an empty JSON payload (e.g., `""`, `"{}"`, or `null`) on a **branch** (identified by a branch path like `"/myBranch"`)
- THEN the TG should test that the returned revision ID after an empty branch commit equals the **current head revision** of that branch (the last committed revision), **NOT the base revision** from which the branch was created.
- Specifically: make two consecutive empty commits on the same branch and verify that the second commit's returned revision is different from the first (i.e., it advances).
- Concretely, the expected behavior is that an empty commit on a branch returns `headRevision` (the latest revision on that branch, e.g., `"0000000000000003"`), not a stale/base revision (e.g., `"0000000000000001"`). The buggy implementation would return the base revision instead.
- Common pitfall 1: Testing empty commits only on a trunk/master branch — the bug specifically manifests on **branches**, not on the trunk.
- Common pitfall 2: Only testing with non-empty content and assuming empty payload is handled identically — the bug is that empty commit logic reuses a stale base revision ID instead of the branch head.
- Common pitfall 3: Not explicitly comparing the returned revision IDs between two consecutive empty branch commits to confirm progression.

### Example (correct test pattern)

```java
// Assume mk is a MicroKernel instance, trunkHead is the head revision on trunk
// First, create a branch
String branchRev1 = mk.commit("/", "+\"myNode\":{}", null, "Create node on trunk");
String branch = mk.branch(branchRev1); // branch path, e.g., "/myBranch"

// Make an empty commit on the branch
String branchRev2 = mk.commit(branch, "", null, "Empty commit 1 on branch");
// Make another empty commit on the branch
String branchRev3 = mk.commit(branch, "", null, "Empty commit 2 on branch");

// Verify progression: branchRev3 should be different from branchRev2
// (each empty commit must advance the branch head)
assertNotNull("Empty branch commit should return a revision", branchRev2);
assertNotNull("Second empty branch commit should return a revision", branchRev3);
assertNotEquals("Empty branch commit must return head revision, not base revision",
    branchRev2, branchRev3);
```

### Example (incorrect — would miss the bug)

```java
// ❌ Only testing trunk, not branches:
String rev1 = mk.commit("/", "", null, "Empty commit on trunk");
String rev2 = mk.commit("/", "", null, "Second empty commit on trunk");
// This may pass even if the branch logic is broken

// ❌ Only testing empty commit on a branch once, without a second one:
String branchRev1 = mk.commit("/", "+\"n\":{}", null, null);
String branch = mk.branch(branchRev1);
String branchRev2 = mk.commit(branch, "", null, "Empty commit");
assertNotNull(branchRev2); // This still passes in buggy version (it returns *something*)
// Need second empty commit to detect regression!
```

### What the test should verify
- Two consecutive empty branch commits must produce **different** revision IDs (progression).
- The second empty commit should NOT return the base revision (the trunk revision at branch creation time).
- In the bug scenario, the failure message was: `expected:<000000000000000[3]> but was:<000000000000000[1]>` — meaning the buggy implementation returned revision `...1` (the base/trunk head) instead of `...3` (current branch head).