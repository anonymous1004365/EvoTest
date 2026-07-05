---
name: partial-memory-page-flush
description: When FixedLengthRecordSorter writes fixed-length records into a MemorySegment
  and the last page is partially filled, a flush operation may write uninitialized
  zero-bytes instead of only the valid records. The test should verify that flush
  produces exactly the expected number of records, catching index-miscalculation bugs
  between the write and flush.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# partial-memory-page-flush

## Instructions

# Partial Memory Page Flush Validation

## Instructions

- WHEN the TG encounters `FixedLengthRecordSorter` writing fixed-length (e.g. 8-byte or 12-byte) records into `MemorySegment` pages, where the total data may not fill the last memory page completely,
- THEN the TG should write a test that **adds a number of records that leaves the last page partially filled** and then **flushes the sorter**, verifying that the flush returns exactly the number of records that were written.
  - For example, if a MemorySegment page is 32 KiB (32,768 bytes) and the record size is 8 bytes, 32,768 / 8 = 4096 records fit per page. Adding 5000 records results in 1 full page (4096 records) plus 904 records in a partial second page. The flush output must contain exactly 5000 records.
  - Use `writeRecord(...)` to add records, then call `writeOutput(...)` or the equivalent flush method to obtain the sorted/flushed output, and assert that the output count equals the input count.
- WHEN verifying the flush output, the TG must **iterate through all flushed records** and **compare each record** with the original records that were written, to ensure no zero-bytes or corrupted data appears at the end of the partial page.
- Common pitfalls:
  - *Pitfall: Verifying only the count of flushed records.* Count alone may pass if the flush miscalculates but still returns the right number of mismatched records. Always verify data content.
  - *Pitfall: Only testing with a record count that exactly fills an integer number of full pages.* The partial-page boundary must be explicitly exercised.
  - *Pitfall: Assuming writeOutput reads from internal structures correctly if direct page iteration works.* The flush path may have a separate indexing calculation.

### Correct example (verifies count AND content at partial-page boundary):

```java
@Test
public void testFlushPartialMemoryPage() throws Exception {
    // Setup: FixedLengthRecordSorter with 32-byte record length, 32 KiB pages
    int pageSize = 32 * 1024;
    int recordLength = 32;
    int fullPages = pageSize / recordLength;
    int extraRecords = 10;  // leaves last page partially filled
    int totalRecords = fullPages + extraRecords;
    
    FixedLengthRecordSorter sorter = createSorter(pageSize, recordLength);
    List<byte[]> writtenRecords = new ArrayList<>();
    
    for (int i = 0; i < totalRecords; i++) {
        byte[] record = new byte[recordLength];
        // fill record with unique data based on index
        Arrays.fill(record, (byte) i);
        sorter.writeRecord(record);
        writtenRecords.add(record);
    }
    
    // Flush
    MutableObjectIterator<byte[]> flushed = sorter.writeOutput(/* serializer */);
    
    // Verify count AND content
    byte[] readRecord;
    int count = 0;
    while ((readRecord = flushed.next()) != null) {
        Assert.assertArrayEquals("Record at index " + count + " was corrupted",
            writtenRecords.get(count), readRecord);
        count++;
    }
    Assert.assertEquals("Flush returned wrong number of records", totalRecords, count);
}
```

### Incorrect example (content not verified, only count):

```java
@Test
public void testFlushTooWeak() throws Exception {
    // BUG: only checks record count, not content
    int totalRecords = 4106;
    FixedLengthRecordSorter sorter = createSorter(32768, 8);
    for (int i = 0; i < totalRecords; i++) {
        sorter.writeRecord(new byte[]{0,1,2,3,4,5,6,7});
    }
    MutableObjectIterator<byte[]> flushed = sorter.writeOutput(/* serializer */);
    int count = 0;
    while (flushed.next() != null) count++;
    Assert.assertEquals(totalRecords, count);  // May pass even if some records are all-zeros!
}
```