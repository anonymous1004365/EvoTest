---
name: stream-record-exact-read-verification
description: When testing blob/stream record read operations from a segment store,
  verify that the data read back exactly matches the original written data byte-for-byte,
  including at boundary sizes like 0, 1, MAX_SEGMENT_SIZE, MAX_SEGMENT_SIZE+1, and
  MAX_SEGMENT_SIZE*2.
code_tags:
- VALIDATION
- STATE_MUTATION
- NULL_CHECK
- RESOURCE_MANAGEMENT
test_pattern: PARAMETRIC_TEST
---

# stream-record-exact-read-verification

## Instructions

# Stream Record Exact Read Verification

## Instructions

- WHEN the TG encounters code that writes blob/stream data to a segment store (e.g., Record.writeStream, SegmentBlob) and then reads it back (e.g., Record.readStream, SegmentBlob.getStream, getNewStream),
  - THEN it should verify the read-back data byte-for-byte matches what was written, for each of these specific sizes: 0, 1, 0x79, 0x80, 16387, MAX_SEGMENT_SIZE, MAX_SEGMENT_SIZE + 1, MAX_SEGMENT_SIZE * 2. Include the actual class-qualified constant (e.g., Segment.MAX_SEGMENT_SIZE) rather than a hardcoded number.

- WHEN the TG writes a test that generates random byte arrays of various sizes and writes them as stream records (e.g., using SegmentWriter.writeStream),
  - THEN it should read the data back using all available stream access methods (e.g., readStream, getNewStream, getBlob, getStream) and compare the full byte content. Simply checking that the read operation doesn't throw an exception is insufficient. The test MUST assert that the content is identical.

- WHEN the TG tests blob/stream record size boundaries that cross segment boundaries (e.g., MAX_SEGMENT_SIZE, MAX_SEGMENT_SIZE + 1),
  - THEN it should produce and verify the data on both sides of the boundary. Create a random byte array of the exact size, write it, read it back, and use Assert.assertArrayEquals to compare the original and read-back data.

- Common pitfalls to avoid:
  - Testing only successful write without reading back and comparing byte content
  - Using hardcoded size constants instead of the class's own boundary constant (e.g., Segment.MAX_SEGMENT_SIZE)
  - Testing only one or two sizes instead of all the boundary values (0, 1, just-above-0, just-below-max-segment, at-max, just-above-max, double-max)
  - Assuming that if no exception is thrown, the data was read correctly — always verify content
  - Forgetting to test edge case sizes that are not powers of 2 (e.g., 0x79, 0x80, 16387)

## Example

### Correct test pattern:
```java
private static void checkRandomStreamRecord(int size) throws Exception {
    byte[] data = new byte[size];
    random.nextBytes(data);
    RecordId id = writer.writeStream(new ByteArrayInputStream(data));
    SegmentBlob blob = new SegmentBlob(store, store.getReader(), id, store.getBlobId());
    byte[] readData;
    try (InputStream stream = blob.getNewStream()) {
        readData = ByteStreams.toByteArray(stream);
    }
    Assert.assertArrayEquals("Data mismatch at size " + size, data, readData);
}

public void testStreamRecord() throws Exception {
    checkRandomStreamRecord(0);
    checkRandomStreamRecord(1);
    checkRandomStreamRecord(0x79);
    checkRandomStreamRecord(0x80);
    checkRandomStreamRecord(16387);
    checkRandomStreamRecord(Segment.MAX_SEGMENT_SIZE);
    checkRandomStreamRecord(Segment.MAX_SEGMENT_SIZE + 1);
    checkRandomStreamRecord(Segment.MAX_SEGMENT_SIZE * 2);
}
```

### Incorrect test pattern (fails to catch the bug):
```java
public void testStreamRecord() throws Exception {
    // Only testing small size, not crossing segment boundaries
    byte[] data = new byte[100];
    random.nextBytes(data);
    RecordId id = writer.writeStream(new ByteArrayInputStream(data));
    // Just checking it doesn't throw — no content verification
    SegmentBlob blob = new SegmentBlob(store, store.getReader(), id, store.getBlobId());
    Assert.assertNotNull(blob.getNewStream());
}
```