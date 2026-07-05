---
name: collect-blob-references-inlined-blob
description: When collecting blob references via Segment.collectBlobReferences(),
  blobs that are inlined (no blobId, stored directly in the segment) can yield null
  references. Tests must verify that null blob references are handled (assertNotNull),
  and that the correct number of references is collected — especially when many blobs
  are mixed with some inlined ones.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# collect-blob-references-inlined-blob

## Instructions

# Collect Blob References with Inlined Blobs

## Instructions

- WHEN the TG encounters code that calls `collectBlobReferences(ReferenceCollector collector)` on a `Segment` or `SegmentTracker` (e.g., `store.getTracker().collectBlobReferences(...)`), and the segment store contains a mix of blobs — some inlined (small enough to be stored directly within the segment, such as blobs smaller than `Segment.MEDIUM_LIMIT`) and some external (blobs larger than or equal to `Segment.MEDIUM_LIMIT`, stored in the external `BlobStore`) — THEN the TG should write a test that:

  1. Creates a `NodeStore` backed by a `DataStoreBlobStore` (or similar external blob store).
  2. Inserts a mix of properties:
     - A small inlined blob (size < `Segment.MEDIUM_LIMIT`), such as `createBlob(Segment.MEDIUM_LIMIT - 1)` or smaller.
     - Many (e.g., 4000) external blobs (size >= `Segment.MEDIUM_LIMIT + 1`) to force segments to overflow.
     - A few external blobs placed after the overflow batch (e.g., `"anotherBlob2"`, `"anotherBlob3"`).
  3. Merges the changes via `nodeStore.merge(...)`.
  4. Calls `collectBlobReferences` and in the `addReference` callback asserts `assertNotNull(reference)` to catch null blob IDs.
  5. Asserts that the total number of collected references equals the expected count of external (non-inlined) blobs only.

- WHEN the TG writes assertions about the number of blob references, THEN it should compute the expected count as the number of properties with external blobs. Inlined blobs (those with `getBlobId() == null`) should NOT be counted as references.

- Common pitfalls:
  - Testing only with a single blob or no overflow: the bug manifests when there are many blobs (causing segment-level boundary conditions), so test with at least hundreds of blobs.
  - Assuming all blobs have non-null references: inlined blobs have `null` blobId and may produce `null` references, causing `collectBlobReferences` to call `addReference(null)`. The test must assert `assertNotNull(reference)` inside the callback.
  - Forgetting to use `DataStoreBlobStore`: pure in-memory stores may not trigger the blob externalization path. Use `FileDataStore` with `DataStoreBlobStore`.

### Correct Example
```java
@Test
public void testNullBlobId() throws Exception {
    FileDataStore fds = createFileDataStore();
    DataStoreBlobStore dbs = new DataStoreBlobStore(fds);
    nodeStore = getNodeStore(dbs);

    NodeBuilder nb = nodeStore.getRoot().builder();
    NodeBuilder cb = nb.child("hello");
    cb.setProperty("blob1", createBlob(Segment.MEDIUM_LIMIT - 1));

    int noOfBlobs = 4000;
    for (int i = 0; i < noOfBlobs; i++) {
        cb.setProperty("blob" + i, createBlob(Segment.MEDIUM_LIMIT + 1));
    }

    cb.setProperty("anotherBlob2", createBlob(Segment.MEDIUM_LIMIT + 1));
    cb.setProperty("anotherBlob3", createBlob(Segment.MEDIUM_LIMIT + 1));
    nodeStore.merge(nb, EmptyHook.INSTANCE, CommitInfo.EMPTY);

    final List<String> references = Lists.newArrayList();
    store.getTracker().collectBlobReferences(new ReferenceCollector() {
        @Override
        public void addReference(String reference) {
            assertNotNull(reference);
            references.add(reference);
        }
    });

    assertEquals(noOfBlobs + 2, references.size());
}
```

### Incorrect Example
```java
// BUG: Does NOT test with a mix of inlined and external blobs
// BUG: Only inserts one blob, does not trigger segment overflow
// BUG: Does not assertNotNull in the callback
@Test
public void testBlobReferences() throws Exception {
    FileDataStore fds = createFileDataStore();
    DataStoreBlobStore dbs = new DataStoreBlobStore(fds);
    nodeStore = getNodeStore(dbs);

    NodeBuilder nb = nodeStore.getRoot().builder();
    NodeBuilder cb = nb.child("hello");
    cb.setProperty("blob1", createBlob(Segment.MEDIUM_LIMIT + 100));
    nodeStore.merge(nb, EmptyHook.INSTANCE, CommitInfo.EMPTY);

    final List<String> references = Lists.newArrayList();
    store.getTracker().collectBlobReferences(new ReferenceCollector() {
        @Override
        public void addReference(String reference) {
            // BUG: no assertNotNull — a null reference would go unnoticed
            references.add(reference);
        }
    });

    assertEquals(1, references.size()); // BUG: may pass even if null was added
}
```