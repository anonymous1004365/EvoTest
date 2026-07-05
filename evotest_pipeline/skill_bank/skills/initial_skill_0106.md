---
name: segment-overflow-list-write
description: When testing large list writes that could overflow a segment boundary,
  test with list sizes near the ListRecord.LEVEL_SIZE boundary (255) to verify the
  writer correctly flushes segments before overflow occurs.
code_tags:
- OVERFLOW
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# segment-overflow-list-write

## Instructions

# Segment Overflow During List Write

## Instructions

WHEN the TG encounters code that writes lists of `RecordId` values via a `SegmentWriter.writeList()` method, and the surrounding code also writes large strings or other records that consume significant segment space:

- THEN the TG should write a parametric test that iterates `n` from 1 to `ListRecord.LEVEL_SIZE - 1` (i.e., 1 to 254) and for each value of `n`, constructs a list of `n` identical `RecordId` references (e.g., via `Collections.nCopies(n, x)`) and calls `writer.writeList(list)`.
- BEFORE calling `writeList(list)`, first ensure the segment has consumed enough space to be near the overflow boundary. Use `writer.writeString(Strings.repeat(...))` to write strings whose total size (in bytes) brings the segment close to the theoretical maximum segment size (around 256KB or `Segment.MAX_SEGMENT_SIZE`).
- AFTER `writeList(list)`, call `writer.flush()` and then `store.close()`.
- Verify that no exception (e.g., `ArrayIndexOutOfBoundsException`, `IllegalArgumentException`, or any `RuntimeException`) is thrown for any value of `n` in the range 1 to 254.
- Common mistake: testing only a single list size or only small lists. The bug manifests specifically when the list write causes the segment buffer to overflow, and this happens only for certain values of `n` when the segment is already nearly full.
- Common mistake: forgetting to close the store after each iteration. Use a try-finally or try-with-resources pattern, but note that if a failure happens, the close must still be attempted.

Example of correct test pattern (in pseudocode):

```java
// Setup store with maxFileSize(1) and memoryMapping(false)
for (int n = 1; n < 255; n++) {
    FileStore store = fileStoreBuilder(folder.newFolder())
        .withMaxFileSize(1)
        .withMemoryMapping(false)
        .build();
    try {
        SegmentWriter writer = store.getWriter();
        // Write 15 strings near MEDIUM_LIMIT-1 bytes each to fill the segment
        for (int k = 0; k < 15; k++) {
            writer.writeString(Strings.repeat(
                "abcdefghijklmno".substring(k, k + 1),
                SegmentTestConstants.MEDIUM_LIMIT - 1));
        }
        // Write an additional large string to approach the overflow threshold
        RecordId x = writer.writeString(Strings.repeat("x", 14278));
        // Write a list of n copies of x — this should trigger flush, not overflow
        List<RecordId> list = Collections.nCopies(n, x);
        writer.writeList(list);
        writer.flush();
    } finally {
        store.close();
    }
}
```

Example of incorrect test pattern (too narrow, misses the bug):

```java
// ❌ Only testing one list size, or small list sizes
for (int n : new int[]{1, 10, 100}) {  // misses the boundary near 255
    ...
}
```