---
name: split-commitroot-migration
description: When splitting document revisions (e.g. after NUM_REVS_THRESHOLD is exceeded),
  _commitRoot entries associated with removed revisions must be migrated to the previous
  document. The TG should write tests that verify all _commitRoot entries are properly
  carried over after a split, not just the ones for revisions that remain locally.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# split-commitroot-migration

## Instructions

# Split Operation Must Migrate All _commitRoot Entries

## Instructions

- **WHEN** the code under test performs a document **split operation** that moves old revisions out of the main document into a previous document (e.g. via `SplitOperations.splitDocument`):
  - **THEN** the test MUST verify that **all** `_commitRoot` entries pointing to the moved/removed revisions are also migrated to the previous document.
  - **THEN** after the split, call `doc.getLocalCommitRoot().keySet()` and verify that it does NOT contain any entries for revisions that were removed from the main document during the split.
  - **THEN** also verify the previously split-off document contains the migrated `_commitRoot` entries that no longer appear in `getLocalCommitRoot()` on the current document.
  - **Common pitfall**: Testing only the count of remaining `_commitRoot` entries without checking that each entry's revision was actually removed. The bug was: after a split removed revisions 1 through 1000, the `_commitRoot` for the removed revisions was not migrated/removed from the main document, leaving stale entries like revision 1001 incorrectly pointing to a `_commitRoot` that should have moved.

- **WHEN** writing a test like `splitCommitRoot()` that creates a document, adds `_commitRoot` entries, triggers a split boundary (e.g. by exceeding `NUM_REVS_THRESHOLD`), and then calls `getLocalCommitRoot()`:
  - **THEN** the test should:
    1. Create a document and add a known set of `_commitRoot` entries (e.g. revisions 1..N where N > threshold).
    2. Trigger the split (e.g. via `SplitOperations.splitDocument()` with a target previous document).
    3. Call `doc.getLocalCommitRoot()` and verify:
       - `getLocalCommitRoot().size()` is 0 (no remaining `_commitRoot` entries) if all revisions were removed, OR
       - `getLocalCommitRoot().keySet()` contains only entries for revisions that were NOT removed.
    4. Check the previous document and verify it received the migrated `_commitRoot` entries.
  - **Common pitfall**: Asserting `getLocalCommitRoot().size() == 0` is insufficient if the test only created a small number of revisions. The bug happened specifically when enough revisions (well past threshold) were created, causing stale `_commitRoot` entries to survive the split.

- **WHEN** the split threshold is `NUM_REVS_THRESHOLD` (e.g. 1000):
  - **THEN** create at least `NUM_REVS_THRESHOLD + 2` revisions to guarantee that a split removes some revisions.
  - **THEN** verify that after the split, `getLocalCommitRoot()` does not contain entries for any revision ≤ (max revision - NUM_REVS_THRESHOLD).

### Correct Example (pseudocode):
```java
// Create document and add 1002 commitRoot entries
for (int i = 1; i <= 1002; i++) {
    Revision r = new Revision(i, 0, 1);
    doc.updateCommitRoot(r, "/path");
}
// Trigger split
newDoc = SplitOperations.splitDocument(doc, prevDoc, new Path("/"), NUM_REVS_THRESHOLD);
// Assert: commitRoots for revs 1-1000 should be migrated
Map<Revision, String> remaining = doc.getLocalCommitRoot();
for (Revision r : remaining.keySet()) {
    assertTrue(r.getTimestamp() > 1000); // only recent entries remain
}
```

### Incorrect Example (the buggy pattern):
```java
// Only creates 1 or 2 commitRoot entries — never triggers the bug
doc.updateCommitRoot(rev1, "/path");
doc.updateCommitRoot(rev2, "/path2");
doc = SplitOperations.splitDocument(doc, prevDoc, new Path("/"), NUM_REVS_THRESHOLD);
// Only checks count — misses that _commitRoot entries weren't migrated
assertEquals(0, doc.getLocalCommitRoot().size());
```