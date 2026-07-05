---
name: branch-commit-rebase-merging-unsaved-revisions
description: When a branch commit has been rebased (using RebaseCommit), accessing
  getBase() must return the base from the rebase chain, not from a fixed constructor
  default. This skill teaches how to test branch commit merging and revision access
  after rebase operations.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# branch-commit-rebase-merging-unsaved-revisions

## Instructions

# Branch Commit Rebase and Revision Access

## Instructions

- WHEN the TG encounters code that creates a `Branch` with a set of commits and a base revision, and then later rebases the branch (via `Branch.rebase(Revision head, Revision base)` which creates a `RebaseCommit`)
- THEN the TG should write a test that:
  1. Creates a `Branch` with multiple initial commits (e.g., `Revision.fromString("r1-0-0")`, `Revision.fromString("r2-0-0")`) and a trunk base revision (e.g., `Revision.fromString("r0-0-0")`)
  2. Rebases the branch using `Branch.rebase(newHead, newBase)` with a new head revision that is after all existing commits and a new trunk base revision
  3. Merges the branch by calling `Branch.applyTo(UnsavedModifications, mergeCommitRevision)` and verifies the resulting modifications use correct base revisions (not the original base)
  4. Verifies that `Branch.getCommit(r).getBase()` returns the correct base revision after the rebase operation, including for the rebased commit itself
- WHEN verifying after a rebase, the test should confirm that `BranchCommit.getBase()` for the rebased commit returns the new rebase base (not the old one from the constructor), and that `BranchCommit.applyTo(UnsavedModifications, mergeCommit)` properly tracks modified paths with correct revisions
- Common pitfalls to avoid:
  - Testing only the constructor case without rebasing — the bug was that after a rebase, accessing the base revision of a branch commit could return stale/wrong data
  - Not testing that `BranchCommit.getBase()` is correctly updated for rebased commits
  - Forgetting that `UnsavedModifications` tracks `_lastRevs` and the test should verify unsaved last revisions after merge
  - Assuming `Branch.Commit.getBase()` always returns the constructor's base without checking rebase effects

### Correct Example

```java
// Create a branch with initial commits
Revision base = Revision.fromString("r0-0-0");
SortedSet<Revision> commits = new TreeSet<Revision>(StableRevisionComparator.INSTANCE);
commits.add(Revision.fromString("r1-0-0"));
commits.add(Revision.fromString("r2-0-0"));
Branch branch = new Branch(commits, base);

// Rebase the branch
Revision rebaseHead = Revision.fromString("r3-1-0"); // branch revision after r2
Revision rebaseBase = Revision.fromString("r5-0-0");  // new trunk base
branch.rebase(rebaseHead, rebaseBase);

// After rebase, a commit created from the rebase should exist
assertNotNull(branch.getCommit(rebaseHead));
// The base of the rebased commit should be the new base
assertEquals(rebaseBase, branch.getCommit(rebaseHead).getBase());
```

### Incorrect Example

```java
// Only testing constructor — misses the rebase bug
Branch branch = new Branch(commits, base);
assertEquals(base, branch.getCommit(rev1).getBase()); // OK, but doesn't test rebase

// Wrong: Checking getBase() returns the constructor's base after rebase
// The default BranchCommitImpl stores base at construction time,
// but RebaseCommit overrides getBase() to return the rebase base.
// A test that only checks the constructor is insufficient.
```