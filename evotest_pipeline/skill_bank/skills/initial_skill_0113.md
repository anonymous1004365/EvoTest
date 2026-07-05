---
name: proxy-delete-non-existent-row
description: When testing delete operations against a proxy or thrift-based storage
  service, verify that deleting a row that does not exist returns a count of 0 (not
  1). This skill catches bugs where the proxy incorrectly returns a non-zero count
  for deletions of non-existent entries.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# proxy-delete-non-existent-row

## Instructions

# Proxy Delete Non-Existent Row

## Instructions

- WHEN the TG encounters a proxy client performing a `deleteRows` (or equivalent) operation on a table
- THEN the TG should write a test that:
  1. Creates a new table or uses an existing empty table
  2. Attempts to delete a row that does NOT exist (e.g., using a row ID like `"row_that_does_not_exist"` or `"non_existent_row"`)
  3. Asserts that the resulting count of deleted entries is exactly `0`
  4. Tests the edge case where no data matches the delete predicate at all (empty result set)

- The test should specifically verify that `client.deleteRows(...)` returns a count of `0` when no rows match the deletion criteria. A buggy proxy implementation may incorrectly return `1` or another non-zero value.

- Common pitfalls:
  - Only testing delete on rows that exist, which would not catch this bug
  - Assuming delete always mutates state (it should return 0 for non-existent)
  - Forgetting to verify the return value/result of the delete operation

- Example (correct approach):
```java
@Test
public void testDeleteNonExistentRow() {
    String table = "testTable";
    client.createTable(table, ...);
    // Delete a row that was never inserted
    long deleted = client.deleteRows(table, "non_existent_row", "non_existent_row");
    assertEquals(0, deleted);
}
```

- Example (incorrect approach — missing this bug):
```java
@Test
public void testDelete() {
    String table = "testTable";
    client.createTable(table, ...);
    // Only testing deletion of existing data
    client.insert(table, ...);
    long deleted = client.deleteRows(table, "existing_row", "existing_row");
    assertEquals(1, deleted);
    // Never tests the empty case
}
```