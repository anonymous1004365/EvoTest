---
name: delete-rows-null-key-validation
description: WHEN a method like MockTableOperations.deleteRows(String, Text, Text)
  accepts nullable parameters (start or end keys), THEN the test should verify passing
  null for each key throws a meaningful exception (e.g., NullPointerException with
  a clear message), not silently corrupt data. Tests must cover both null-start and
  null-end cases independently.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- NULL_ARGUMENT_HANDLING
test_pattern: EXCEPTION_TEST
---

# delete-rows-null-key-validation

## Instructions

# Delete Rows Null Key Validation

## Instructions

- WHEN the TG encounters a method `deleteRows(String tableName, Text start, Text end)` or any method that accepts nullable range-boundary parameters (e.g., `Text start`, `Text end`) in a mock or implementation class
- THEN the TG should test that passing `null` for each boundary parameter individually throws an appropriate exception (e.g., `NullPointerException`) — NOT silently processes the request or leaves state inconsistent
- The TG should create a test that:
  1. Creates a table and inserts data
  2. Calls `deleteRows(tableName, new Text("valid"), null)` — expecting a `NullPointerException`
  3. Calls `deleteRows(tableName, null, new Text("valid"))` — expecting a `NullPointerException`
- **Common Pitfall**: Testing only one null parameter (e.g., only `end=null`) but missing the other (e.g., `start=null`). Both `start` and `end` can independently be null per the interface signature, and the method must handle (or reject) both.
- **Common Pitfall**: Assuming null means "open-ended range" (which Accumulo's `deleteRows` does NOT support — null should be rejected explicitly). Do NOT test that null is accepted; test that it throws.
- The test should verify the exception is thrown before the method mutates any state (e.g., the table's row count should still match the inserted data after the exception).

### Correct Example

```java
@Test
public void testDeleteRowsWithNullStart() throws Exception {
    // setup: create table with data
    String tableName = "testNullStart";
    conn.tableOperations().create(tableName);
    BatchWriter bw = conn.createBatchWriter(tableName, new BatchWriterConfig());
    Mutation m = new Mutation("row1");
    m.put("cf", "cq", "v1");
    bw.addMutation(m);
    bw.close();

    // null start key should throw
    assertThrows(NullPointerException.class, () -> {
        conn.tableOperations().deleteRows(tableName, null, new Text("row2"));
    });

    // verify data still present (method did not silently delete)
    Scanner scanner = conn.createScanner(tableName, Authorizations.EMPTY);
    assertTrue(scanner.iterator().hasNext());
    scanner.close();
    conn.tableOperations().delete(tableName);
}

@Test
public void testDeleteRowsWithNullEnd() throws Exception {
    // setup: create table with data
    String tableName = "testNullEnd";
    conn.tableOperations().create(tableName);
    BatchWriter bw = conn.createBatchWriter(tableName, new BatchWriterConfig());
    Mutation m = new Mutation("row1");
    m.put("cf", "cq", "v1");
    bw.addMutation(m);
    bw.close();

    // null end key should throw
    assertThrows(NullPointerException.class, () -> {
        conn.tableOperations().deleteRows(tableName, new Text("row1"), null);
    });

    conn.tableOperations().delete(tableName);
}
```

### Incorrect Example (would miss the bug)

```java
@Test
public void testDeleteRowsOnlyNullEnd() throws Exception {
    // Only tests null end, missing null start!
    assertThrows(NullPointerException.class, () -> {
        conn.tableOperations().deleteRows("test", new Text("1"), null);
    });
    // Missing: test with null start
}

@Test
public void testDeleteRowsWithInvalidKeys() throws Exception {
    // Using empty Text or invalid range, but NOT testing null
    conn.tableOperations().deleteRows("test", new Text(""), new Text(""));
    // Does not verify null handling at all
}
```