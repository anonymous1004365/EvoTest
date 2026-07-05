---
name: external-blob-segment-store-mutation
description: When adding binary properties to a segment store that uses an external
  blob store, tests must verify that only the blob record id is persisted — not the
  blob data itself. External blob references should not be duplicated into the segment
  store's internal data.
code_tags:
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# external-blob-segment-store-mutation

## Instructions

# External Blob Segment Store — Reference-Only Persistence

## Instructions

WHEN the TG encounters code that writes binary property values (blobs) to a segment store backed by an external blob store (e.g., `SegmentWriter.writeBlob()`, `DefaultSegmentWriter.writeBlob()`, or similar methods that accept `Blob` objects), THEN:

1. **Test that binary property data stored in the external blob store is NOT duplicated** into the segment store's internal segment data. The segment should only reference the blob by its `RecordId` — the blob bytes should live exclusively in the external store.

2. **Create a test that:**
   - Writes a blob to an external `BlobStore` via `blobStore.writeBlob(...)` to get a blob ID
   - Creates a `Blob` object by reading back from the blob store using `blobStore.getBlob(blobId)`
   - Passes that `Blob` into `segmentWriter.writeBlob(blob)` to persist as a binary property in the segment
   - Serializes the segment (flushes to an in-memory segment store)
   - Reads back the binary property — either via parsing the segment or using a `NodeState`-like API
   - **Asserts that the read-back property references the original blob ID**, not a copy of the data
   - **Asserts that the actual blob data resides in the external blob store**, not in the segment

3. **Key verification:**
   - Use an in-memory segment store implementation (e.g., `SegmentNodeStoreService` or a custom `InMemoryBlobStore`)
   - Call `blobStore.writeBlob(stream)` and verify the blob ID before writing to the segment
   - After writing to the segment, call `blobStore.getBlob(blobId)` to confirm the data is still accessible
   - Parse the segment binary property and assert it returns the same `RecordId` pointing to the external blob, not an inline copy

4. **Common pitfalls:**
   - ❌ Testing only with `Blob` objects created from inline data (e.g., `new ByteArrayInputStream(...)` without going through the external blob store first) — this won't detect the duplication bug
   - ❌ Only verifying that `writeBlob()` returns a non-null `RecordId` without checking the content of the segment
   - ❌ Not flushing or persisting the segment before reading back the data
   - ❌ Assuming that `writeBlob()` on a `SegmentWriter` automatically delegates correctly to the external store without verifying the segment's binary property representation
   - ❌ Not using both `String` and `CtTypeReference` types (or whatever parameterization the API supports) when the API is type-generic

5. **Correct approach:**
   ```java
   BlobStore externalBlobStore = new InMemoryBlobStore();
   String blobId = externalBlobStore.writeBlob(new ByteArrayInputStream("test data".getBytes(StandardCharsets.UTF_8)));
   Blob blob = externalBlobStore.getBlob(blobId);
   RecordId recordId = segmentWriter.writeBlob(blob);
   // flush/persist segment
   // read back binary property from segment and assert it references blobId, not inline data
   assertNotNull(recordId);
   // parse the segment's binary property record
   // verify that parsing yields a reference to the external blob, not embedded data
   ```

6. **Incorrect approach (won't catch the bug):**
   ```java
   // BAD: Creates blob directly without going through external store
   Blob blob = new ByteArrayInputStream("test data".getBytes(StandardCharsets.UTF_8));
   RecordId recordId = segmentWriter.writeBlob(blob);
   assertNotNull(recordId);
   // This test passes even if the buggy code duplicates blob data into the segment
   ```