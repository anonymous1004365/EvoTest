---
name: multi-level-list-reference-bucket-boundary
description: When writing a multi-level list (list of RecordId references) that gets
  split into buckets, the bucket boundary logic may produce duplicate records when
  indexing past the first level. Use a large list of unique RecordId values to test
  that the list size and all references remain correct.
code_tags:
- STATE_MUTATION
- BOUNDARY_CHECK
- ARRAY_INDEX_ACCESS
test_pattern: PARAMETRIC_TEST
---

# multi-level-list-reference-bucket-boundary

## Instructions

# Multi-Level List Reference Bucket Boundary

## Instructions

- WHEN the TG encounters a `writeList(List<RecordId>)` method that splits a list into buckets for multi-level storage (e.g. `DefaultSegmentWriter.writeList()` with bucket size limits like `LIST_BUCKET_SIZE`)
- THEN the TG should test with a list that contains **more than `LIST_BUCKET_SIZE` unique `RecordId` entries** (e.g. 101+ entries when `LIST_BUCKET_SIZE = 100`), where each entry is a **distinct** `RecordId` (e.g. created with `new RecordId(idProvider.newBulkSegmentId(), 0)`). Verify that:
  - The returned `RecordId`'s segment can be read back
  - The list read back has exactly the expected size (`list.size()`)
  - All individual entries can be retrieved correctly via `list.getEntry(i)` and match the original values
- WHEN testing multi-level list writes, the TG must verify that **the number of references stored matches the number of input entries**, especially when the input list size causes the list to span multiple levels (buckets → next-level list of bucket references). The bug is that a reference-count expression (e.g. `(size + 1) / 2`) can produce an incorrect count for non-power-of-two sizes, causing missing entries when the list is read back later.
- Common pitfalls to avoid:
  - **Testing only with a small list** (fewer entries than bucket size) — this exercises only the single-level path and won't trigger the multi-level indexing bug
  - **Using duplicate references** (same `RecordId` repeated) — the bug manifests when comparing *counts* of unique entries; duplicates mask the off-by-one or truncation issue
  - **Only checking `list.size()`** without also checking each entry — the size may appear correct while entries beyond a certain index are wrong or null
  - **Using power-of-two sizes** (e.g. 100, which is exactly `LIST_BUCKET_SIZE`) — the bug may only trigger when `size` is not evenly divisible by the bucket size

### Correct example (catching the bug):
```java
@Test
public void testListWithLotsOfReferences() throws Exception {
    SegmentIdProvider idProvider = store.getSegmentIdProvider();
    List<RecordId> list = new ArrayList<>();
    for (int i = 0; i < 101; i++) { // More than LIST_BUCKET_SIZE (100)
        list.add(new RecordId(idProvider.newBulkSegmentId(), 0));
    }
    RecordId listId = writer.writeList(list);
    ListRecord r = new ListRecord(store.getSegmentReader(), listId, list.size());
    assertEquals("List size must match", list.size(), r.size());
    for (int i = 0; i < list.size(); i++) {
        assertEquals("Entry " + i + " must match input",
            list.get(i), r.getEntry(i));
    }
}
```

### Incorrect example (missing the bug):
```java
@Test
public void testListWithReferences() throws Exception {
    SegmentIdProvider idProvider = store.getSegmentIdProvider();
    List<RecordId> list = new ArrayList<>();
    for (int i = 0; i < 50; i++) { // Too few entries — only one level
        list.add(new RecordId(idProvider.newBulkSegmentId(), 0));
    }
    RecordId listId = writer.writeList(list);
    ListRecord r = new ListRecord(store.getSegmentReader(), listId, list.size());
    assertEquals("size matches", list.size(), r.size());
    // Only checks size, and with < 100 entries the bug doesn't trigger
}
```