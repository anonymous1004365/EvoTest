---
name: copy-on-write-lock-verification
description: When a LuceneIndexEditorProvider is reused across multiple commits with
  an IndexCopier that uses copy-on-write, tests must verify that concurrent commits
  do not corrupt shared state. Use this when testing IndexEditorProvider instances
  with shared IndexCopier/IndexTracker state.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- ARRAY_INDEX_ACCESS
- CONCURRENCY
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# copy-on-write-lock-verification

## Instructions

# Copy-on-Write Lock Verification for IndexEditorProvider

## Instructions

- WHEN the TG encounters a `LuceneIndexEditorProvider` (or any `IndexEditorProvider`) that is reused across multiple commits with a shared `IndexCopier` and `IndexTracker` that performs copy-on-write operations on the Lucene directory
- THEN the TG should write a test that exercises the full lifecycle of multiple sequential commits, verifying that locks acquired during indexing are properly released and that the `IndexCopier`'s copy-on-write mechanism does not deadlock or throw `OakLucene0003: Failed to index the node`
- Use the following concrete pattern:
  1. Create a single `LuceneIndexEditorProvider` instance
  2. Create an `EditorHook` that wraps it via `IndexUpdateProvider`
  3. Call `HOOK.processCommit(before, after, CommitInfo.EMPTY)` for at least 3–5 sequential commits, modifying different nodes each time (e.g., add `/test1`, `/test2`, `/test3`)
  4. After each commit, update the `IndexTracker` via `tracker.update(indexed)`
  5. Verify that each commit succeeds without `CommitFailedException` and that the Lucene directory can be queried after each commit (e.g., using `DirectoryReader.open(directory)` or `getPath(new TermQuery(...))`)
- Expect that the buggy version will throw `OakLucene0003: Failed to index the node /test` starting from the second commit, because the `IndexCopier` holds a lock on the local directory that prevents the next indexing operation from opening a new writer
- Common pitfalls:
  - ❌ Testing with only a single commit — this masks the bug because the lock leak only manifests on the **second** write
  - ❌ Creating a new `IndexEditorProvider` or `EditorHook` for each commit — this bypasses the shared state issue
  - ❌ Not updating the `IndexTracker` between commits — the tracker must reflect the previous commit's state for the bug to trigger
  - ❌ Using `@Before` or `@Rule` that resets the provider/tracker — this hides the accumulated lock state

### Correct Example (excerpt based on the triggering test `copyOnWriteAndLocks`):

```java
private static final EditorHook HOOK = new EditorHook(
        new IndexUpdateProvider(new LuceneIndexEditorProvider()));

public void copyOnWriteAndLocks() throws Exception {
    NodeBuilder builder = root.builder();
    NodeBuilder index = builder.child(INDEX_DEFINITIONS_NAME);
    NodeBuilder idxnb = newLuceneIndexDefinitionV2(index, "lucene",
            ImmutableSet.of(TYPENAME_STRING));
    IndexDefinition defn = new IndexDefinition(root, idxnb.getNodeState());
    
    // Commit 1 - should succeed
    NodeState before = builder.getNodeState();
    builder.child("test1").setProperty("foo", "fox is jumping");
    NodeState after = builder.getNodeState();
    NodeState indexed = HOOK.processCommit(before, after, CommitInfo.EMPTY);
    tracker.update(indexed);
    assertEquals("/test1", getPath(new TermQuery(new Term("foo", "fox is jumping"))));
    
    // Commit 2 - triggers lock leak bug → OakLucene0003
    before = builder.getNodeState();
    builder.child("test2").setProperty("bar", "kite is flying");
    after = builder.getNodeState();
    indexed = HOOK.processCommit(before, after, CommitInfo.EMPTY);
    tracker.update(indexed);
    assertEquals("/test2", getPath(new TermQuery(new Term("bar", "kite is flying"))));
    
    // Commit 3 - verify further commits also work
    before = builder.getNodeState();
    builder.child("test3").setProperty("baz", "sun is shining");
    after = builder.getNodeState();
    indexed = HOOK.processCommit(before, after, CommitInfo.EMPTY);
    tracker.update(indexed);
    assertEquals("/test3", getPath(new TermQuery(new Term("baz", "sun is shining"))));
}
```

### Incorrect Example (single commit — misses the bug):

```java
// ❌ Only one commit — never detects the lock leak
public void testBasicIndexing() throws Exception {
    NodeState before = builder.getNodeState();
    builder.child("test").setProperty("foo", "fox is jumping");
    NodeState after = builder.getNodeState();
    NodeState indexed = HOOK.processCommit(before, after, CommitInfo.EMPTY);
    tracker.update(indexed);
    assertEquals("/test", getPath(new TermQuery(new Term("foo", "fox is jumping"))));
}
```