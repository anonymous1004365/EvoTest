---
name: proxy-delete-mutation-validation
description: When writing tests for proxy delete operations that use a shared mutation
  writer with batch() and execute(), the test must verify the mutation is fully applied
  by scanning the table, not just checking the writer's return value. This skill catches
  bugs where mutations are silently lost or ignored during delete operations.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# proxy-delete-mutation-validation

## Instructions

# Proxy Delete Mutation Validation

## Instructions

- WHEN the TG encounters a proxy-based test that writes data via `client.createWriter()`, uses `writer.addMutations()` or `writer.update()`, and then calls `client.executeWriter()` or `writer.execute()` before performing a delete operation
- THEN the TG should verify that (1) the data was actually written to the table by performing a scan or query before the delete, (2) the delete operation targets the correct range/row, and (3) after the delete, a scan confirms the data was removed. The test should assert that the row count changes from 1 to 0 (i.e., `assertEquals(1, ...)` before delete and `assertEquals(0, ...)` after delete). The failure message "expected:<1> but was:<0>" indicates the initial write did not persist the mutation correctly.

- WHEN the TG uses `client.batchWriterOperations()` or the proxy writer API with `openWriter()`, `applyUpdates()`, and `closeWriter()`
- THEN the TG must ensure that the writer is properly closed/flushed before performing subsequent operations like scanning or deleting. A common pitfall is calling `executeWriter()` but assuming the mutations were applied when they may have been silently dropped due to a range mismatch, column family mismatch, or missing iterator configuration. The test should insert a known value, verify it exists via scan, delete it, then verify the scan returns zero results.

**Common pitfalls to avoid:**
- Testing the delete without first confirming the write succeeded — the proxy API may silently fail on writes, making the delete appear to work when it actually deletes nothing.
- Using only `writer.execute()` return value without scanning to confirm the mutation was applied — the return value may be empty even though the write failed.
- Forgetting to flush/close the writer before performing scans or deletes — proxy writers may buffer mutations.

**Correct example pattern:**
```java
// Write data
ByteBuffer writer = client.createWriter(login, table, new WriterOptions());
List<ColumnUpdate> updates = new ArrayList<>();
updates.add(new ColumnUpdate(ByteBuffer.wrap("cf".getBytes()), ByteBuffer.wrap("cq".getBytes()),
    false, ByteBuffer.wrap("value".getBytes()), null));
client.updateAndFlush(writer, ByteBuffer.wrap("row1".getBytes()), updates);
// Verify write
ScanResult before = client.startScan(login, table, new ScanOptions());
List<KeyValue> beforeResults = before.getResults();
assertEquals("Expected data to be written before delete", 1, beforeResults.size());
// Close scanner
client.closeScan(before.getScanner());
// Perform delete
client.deleteRows(login, table, ByteBuffer.wrap("row1".getBytes()), ByteBuffer.wrap("row1".getBytes()));
// Verify delete
ScanResult after = client.startScan(login, table, new ScanOptions());
List<KeyValue> afterResults = after.getResults();
assertEquals("Expected data to be deleted", 0, afterResults.size());
client.closeScan(after.getScanner());
```

**Incorrect example (missing write verification):**
```java
// Write data
ByteBuffer writer = client.createWriter(login, table, new WriterOptions());
// ... update and flush ...
// Delete without confirming write succeeded
client.deleteRows(login, table, range);
// This never fails because the write was silently lost
assertEquals(0, scanResults.size());
```