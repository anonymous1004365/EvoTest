---
name: proxy-delete-after-mutation-verification
description: Use when testing proxy delete operations that depend on prior state mutations
  (like insert/update). Verify that a delete operation actually removes the expected
  number of entries by checking the count before and after, and that the count decreases
  by exactly the number of rows that were previously inserted.
code_tags:
- VALIDATION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# proxy-delete-after-mutation-verification

## Instructions

# Proxy Delete After Mutation Verification

## Instructions

- WHEN the TG encounters a proxy delete method that deletes rows from a table (e.g., `deleteRows`, `deleteRange`, or any method that removes entries based on a range/prefix)
- THEN the TG should write a test that:
  1. Inserts a known number of entries (e.g., 2 entries with specific row IDs)
  2. Counts the entries in the table to establish a baseline
  3. Calls the delete operation and then counts again
  4. Verifies the count decreased by the exact expected number (e.g., from 1 to 0 after deleting the only entry that was inserted)

- WHEN the TG constructs the delete request for a proxy table operation
- THEN the TG should use the same table instance (e.g., `ITableOperations` obtained from a `TableOperationsHelper`) and verify that the table still exists after deletion

- WHEN writing the test assertions
- THEN the TG should check:
  - The count of remaining entries after delete equals `expectedCountBeforeDelete - numberOfDeletedEntries`
  - Use `assertEquals(expected, actual)` style assertions that would fail on the buggy version (e.g., expecting 0 entries but getting 1)

- Common pitfalls to avoid:
  - Testing delete without first inserting data, which masks the bug
  - Checking only that delete does not throw an exception instead of verifying the data removal
  - Using a different table or context for insert vs. delete operations
  - Failing to close the batch writer or scanner before performing the count

### Example (correct)

```java
@Test
public void testDelete() throws Exception {
  // Obtain proxy client and table operations
  ProxyServer.Iface client = ...;
  
  // Insert entries
  client.updateAndFlush(tableName, createMutations("row1", "row2"));
  
  // Count before delete
  int countBefore = countEntries(client, tableName);
  
  // Delete the rows
  client.deleteRows(tableName, createRange("row1"));
  
  // Count after delete
  int countAfter = countEntries(client, tableName);
  
  // Verify the count decreased by the expected amount
  assertEquals(countBefore - 1, countAfter);
}
```

### Example (incorrect — misses the bug)

```java
@Test
public void testDelete() throws Exception {
  // BAD: No entries inserted before delete
  ProxyServer.Iface client = ...;
  
  // Delete without prior insertion
  client.deleteRows(tableName, createRange("row1"));
  
  // BAD: Only checks no exception — does not verify actual removal
  // No assertion on entry count
}
```