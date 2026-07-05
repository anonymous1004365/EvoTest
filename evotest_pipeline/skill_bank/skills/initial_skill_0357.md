---
name: blob-id-bounded-length-validation
description: When writing external blob references with blobId length constraints,
  test that blobIds at or beyond the BLOB_ID_SMALL_LIMIT boundary correctly trigger
  an IllegalArgumentException. This skill applies to segment storage code that writes
  blob IDs with length-dependent routing.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# blob-id-bounded-length-validation

## Instructions

# Blob ID Bounded Length Validation

## Instructions

- WHEN the TG encounters code that writes a blob ID (blobId) and the implementation uses `Segment.BLOB_ID_SMALL_LIMIT` to decide the serialization path (small vs. large)
- THEN the TG should write an `@Test(expected = IllegalArgumentException.class)` test that constructs a blobId whose length is **equal to** `Segment.BLOB_ID_SMALL_LIMIT` and attempts to serialize it. The test must verify that an `IllegalArgumentException` is thrown, confirming the boundary check works correctly.

- The buggy code in `RecordWriters.java`'s `SmallBlobIdWriter` uses `checkArgument(blobId.length < Segment.BLOB_ID_SMALL_LIMIT)` — note the strict **less-than** comparison (`<`). A blobId whose length **equals** `Segment.BLOB_ID_SMALL_LIMIT` should be rejected, while lengths strictly less than the limit should be accepted and lengths greater than or equal to the limit should go through the large blob ID writer instead.

- **Common pitfall**: Testing only with blobIds significantly longer than the limit (e.g., 2x the limit) misses the boundary case where the length is *exactly* the limit. The bug was triggered precisely at the boundary where length == `BLOB_ID_SMALL_LIMIT`.

- **Example (correct)**:
```java
// Build a blobId string whose length exactly equals the limit
String blobId = Strings.repeat("x", Segment.BLOB_ID_SMALL_LIMIT);
// Expect an exception because length is NOT less than BLOB_ID_SMALL_LIMIT
new DefaultSegmentWriter(...).writeBlobId(blobId); // expects IllegalArgumentException
```

- **Example (incorrect — misses the exact boundary)**:
```java
// Testing only lengths far above the limit:
String blobId = Strings.repeat("x", Segment.BLOB_ID_SMALL_LIMIT + 1000);
// This goes through the large writer and doesn't test the boundary check
```

- **Mistake to avoid**: Do NOT assume the boundary check is `<=` — verify it is actually `<` or `<=` by examining `checkArgument` calls. Also avoid testing only one side of the boundary (e.g., only very long blobIds or only very short blobIds).

- The triggering test class `ExternalBlobReferenceTest` uses `SegmentTestConstants.BLOB_ID_SMALL_LIMIT` as a convenient reference constant equal to `Segment.BLOB_ID_SMALL_LIMIT`.