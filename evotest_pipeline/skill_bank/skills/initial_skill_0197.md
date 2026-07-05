---
name: blob-store-count-delete-chunks-state-mutation
description: WHEN testing RDBBlobStore or AbstractBlobStore implementations that track
  delete-chunk counts via countDeleteChunks, THEN verify that the count reflects the
  correct number of actually deleted chunks and does not include entries that were
  already deleted. This skill prevents bugs where the count state gets out of sync
  with actual stored data.
code_tags:
- RESOURCE_MANAGEMENT
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# blob-store-count-delete-chunks-state-mutation

## Instructions

# Blob Store Count Delete Chunks State Mutation

## Instructions

WHEN the TG encounters a `BlobStore` implementation (such as `RDBBlobStore` or any subclass of `AbstractBlobStore`) that supports `countDeleteChunks(List<String> chunkIds, long maxLastModifiedTime)`:
- THEN the TG should write a STATE_TEST that verifies state consistency between the delete count and actual existence of data
- Specifically, WHEN calling `countDeleteChunks()` with a list of chunk IDs, THEN the TG should verify that:
  1. The returned count equals the number of chunks that actually existed at the time of deletion
  2. Calling `countDeleteChunks()` AGAIN with the SAME chunk IDs (after the first deletion) returns 0
  3. The count is not inflated by re-deleting already-deleted chunks
- The TG should test with at least these scenarios:
  1. **Normal deletion**: Store blocks, delete them via `deleteChunks()`, call `countDeleteChunks()` — verify count > 0
  2. **Re-deletion (state mutation bug)**: After deleting chunks, call `countDeleteChunks()` again with the same chunk IDs — verify count is 0 (not counting already-deleted entries again)
  3. **Mixed existence**: Delete some chunks but not others, then call `countDeleteChunks()` — verify it counts only the ones that existed

WHEN the TG is testing a `BlobStore` that stores blocks via `storeBlock(byte[] digest, int level, byte[] data)` and reads via `readBlock(byte[] digest)`:
- THEN the TG should verify that after deleting a block and attempting to read it, `readBlock()` either returns `null` or throws a meaningful exception indicating the block is gone
- THEN the TG should verify that after calling `countDeleteChunks()` with the deleted block's ID, the count is accurate (1 for first call, 0 for second call with same IDs)

Common pitfalls to avoid:
- **Testing only the happy path**: Do NOT assume that calling `countDeleteChunks()` only once is sufficient. The bug manifests on the SECOND call with the same chunk IDs, where the count should return 0 but returns > 0 instead
- **Forgetting to check actual data state**: Do NOT just check that the count is non-negative — verify that the chunks actually get deleted from the backend storage (e.g., by attempting to read them)
- **Confusing `deleteChunks()` with `countDeleteChunks()`**: `deleteChunks()` actually removes the data; `countDeleteChunks()` should report how many were removed but should not count already-removed chunks again
- **Using only unit-level mocking**: This bug involves real database interaction (in RDBBlobStore), so prefer integration tests with a real database backend (H2 in-memory) rather than mocked SQL

### Example (Correct):
```java
// Test that countDeleteChunks correctly reports zero on re-deletion
// (this catches the bug where state is mutated incorrectly)
byte[] data = "test data".getBytes("UTF-8");
byte[] digest = MessageDigest.getInstance("SHA-256").digest(data);

// Store a block
RDBBlobStoreFriend.storeBlock(store, digest, 0, data);

// First deletion — should delete it
long count1 = store.countDeleteChunks(
    ImmutableList.of(Hex.encodeHexString(digest)), 0);
assertTrue("First count should be > 0", count1 > 0);

// Second deletion with same IDs — the buggy version returns > 0 again
// because it's counting already-deleted entries
long count2 = store.countDeleteChunks(
    ImmutableList.of(Hex.encodeHexString(digest)), 0);
assertEquals("Re-deletion should return 0", 0, count2);
```

### Example (Incorrect - misses the bug):
```java
// BAD: Only tests that countDeleteChunks returns something
// This passes on both buggy and fixed versions, so it doesn't catch the bug
byte[] data = "test data".getBytes("UTF-8");
byte[] digest = MessageDigest.getInstance("SHA-256").digest(data);
RDBBlobStoreFriend.storeBlock(store, digest, 0, data);

long count = store.countDeleteChunks(
    ImmutableList.of(Hex.encodeHexString(digest)), 0);
assertTrue("Count should be non-negative", count >= 0);
// Missing: second call with same IDs to verify state is correct
```