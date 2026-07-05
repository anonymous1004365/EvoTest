---
name: hash-table-spill-without-overflow-segments
description: When testing hash table implementations that manage memory through linked
  partition buffers and overflow segments, verify that the table can spill partitions
  to disk even when no overflow segments are available and only partition buffers
  remain. This prevents deadlock scenarios during probing phase.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- RESOURCE_MANAGEMENT
- STATE_MUTATION
- ARRAY_INDEX_ACCESS
test_pattern: STATE_TEST
---

# hash-table-spill-without-overflow-segments

## Instructions

# Hash Table Spill Without Overflow Segments

## Instructions

WHEN you encounter a `MutableHashTable` (or similar hash table with memory management using `MemorySegment` lists, partition buffers, and overflow buckets) where:
- The table constructor takes a `List<MemorySegment>` for memory and manages partition buffers + overflow segments from a shared pool
- The table is initialized with the minimum number of segments (e.g., 33 segments of size 128 bytes)
- Records are large (e.g., `byte[]` arrays with lengths exceeding the page size), causing each record to consume an entire partition buffer immediately
- No overflow buckets are created because each record fills its own partition buffer segment

THEN you must write a test that:
1. Uses a small page size (e.g., 128 bytes) and the minimum number of segments (e.g., 33) to create tight memory conditions
2. Uses large records (e.g., `byte[]` arrays with length > page size - header overhead) such that each inserted record consumes an entire partition buffer without creating overflow segments
3. Inserts enough build-side records to fully consume all partition buffers (e.g., 9 records where there are only enough segments for ~9 partitions)
4. Calls `nextRecord()` on the probe side and iterates the build-side matches to force probing
5. Verifies that the table does NOT throw an unexpected `RuntimeException` (e.g., one containing "exceeded maximum number of recursions" is acceptable, but other exceptions should cause test failure)
6. Verifies that the table completes without hanging or deadlocking

**Common pitfalls to avoid:**
- Testing only with small records that naturally create overflow segments — the bug manifests precisely when overflow segments are absent
- Using too many memory segments (e.g., 34+ with large page sizes) which masks the memory pressure condition
- Not iterating the build side matches during probing — the deadlock occurs only when probing actually accesses the spilled partitions
- Forgetting to close the table in a `finally` block or verify temp file cleanup via `checkNoTempFilesRemain(ioMan)`

**Correct example (simplified):**
```java
final int pageSize = 128;
final int numSegments = 33;  // minimum segments
List<MemorySegment> memory = getMemory(numSegments, pageSize);
MutableHashTable<byte[], byte[]> table = new MutableHashTable<>(
    serializer, serializer, buildComparator, probeComparator,
    pairComparator, memory, ioMan, 1, false);

// Insert large records that fill partition buffers without overflow
int numElements = 9;
table.open(new LargeRecordIterator(numElements), new ProbeIterator(1));

try {
    while (table.nextRecord()) {
        MutableHashTable.HashBucketIterator<byte[], byte[]> matches = table.getBuildSideIterator();
        while (matches.next() != null);
    }
} catch (RuntimeException e) {
    if (!e.getMessage().contains("exceeded maximum number of recursions")) {
        fail("Unexpected exception: " + e.getMessage());
    }
} finally {
    table.close();
}
checkNoTempFilesRemain(ioMan);
```

**Incorrect example:**
```java
// Too many segments, too large pages — no memory pressure
final int pageSize = 32*1024;
final int numSegments = 128;
List<MemorySegment> memory = getMemory(numSegments, pageSize);
// This configuration will always work and never trigger the spilling bug
```