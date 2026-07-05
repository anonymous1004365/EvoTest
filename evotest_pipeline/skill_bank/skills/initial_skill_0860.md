---
name: purge-revisions-exception-on-merge
description: When testing document store cleanup operations that purge revision data
  (like split operations), verify that concurrent or subsequent merge operations on
  affected documents correctly throw CommitFailedException rather than succeeding
  and corrupting state.
code_tags:
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# purge-revisions-exception-on-merge

## Instructions

# Purging Old Revisions Must Not Break Subsequent Merges

## Instructions

- WHEN the test performs a document store cleanup operation that removes old revisions (e.g., purging all but the most recent committed commit root) on a document that also has uncommitted branch revisions
- THEN the test MUST also perform a subsequent merge operation on the same document that has uncommitted branch revisions, and verify that the merge correctly throws a `CommitFailedException` with the message "merge must fail with CommitFailedException" or similar conflict/transaction failure
- Specifically, the test should: (1) create a document with multiple committed revisions plus a pending uncommitted branch revision, (2) run a purge/cleanup that removes all old committed revisions, (3) merge the branch, and (4) assert that the merge throws `CommitFailedException`

### Common pitfalls
- Testing only that the purge operation itself succeeds, without verifying that affected branch commits fail correctly
- Using `@Test(expected=...)` on the purge method call instead of a separate merge step
- Not checking that the exception type is `CommitFailedException` (or a subclass thereof)
- Failing to ensure both committed revisions AND uncommitted branch revisions exist on the same document before purge

### Example: Correct approach

```java
@Test
public void purgeAllButMostRecentCommittedCommitRoot() throws Exception {
    // Create situation: committed revisions + branch revision on same document
    // ... setup code ...
    
    // Perform the purge
    /* service.purgeAllButMostRecentCommittedCommitRoot() */;
    
    // VERIFY: merging the branch MUST fail
    try {
        /* branch.merge() or similar */;
        fail("merge must fail with CommitFailedException");
    } catch (CommitFailedException e) {
        // expected
    }
}
```

### Example: Wrong approach (missing the post-purge merge assertion)

```java
@Test
public void purgeAllButMostRecentCommittedCommitRoot() {
    // Only tests the purge, no check on merge behavior
    /* service.purgeAllButMostRecentCommittedCommitRoot() */;
    // Missing: merge the branch and expect CommitFailedException
}
```