---
name: delete-rows-truncates-table
description: When testing row deletion operations that accept start/end row boundaries,
  verify that deleting all rows (e.g. with null start/end) correctly removes all data.
  Without this test, implementations may silently use incorrect comparison logic that
  fails to delete rows.
code_tags:
- STATE_MUTATION
- VALIDATION
- DELETEROWS_NULL_CHECK
test_pattern: STATE_TEST
---

# delete-rows-truncates-table

## Instructions

# Delete Rows With Null Boundaries Truncates Table

## Instructions

- WHEN the TG encounters a `deleteRows(String tableName, Text start, Text end)` method (or similar method for deleting a range of rows) that can accept `null` for start and/or end boundaries
- THEN the TG should write a test that:
  1. Inserts multiple rows into a table with known values
  2. Calls `deleteRows` with `null` start and `null` end (representing "delete all rows")
  3. Verifies that the table is now empty — the row count is zero after deletion
  4. As a secondary check, verify the table still exists (deleting all rows should NOT drop the table)
- Common pitfalls to avoid:
  - Testing `deleteRows` only with non-null boundaries (start/end set to specific values) — this misses the null-boundary case
  - Assuming the table must have entries before testing full deletion — actually, also test that repeated deletion (deletion on an already-empty table) does not throw an exception
  - Assuming the table name is cached or referenced elsewhere — test uses the same table identifier for both insertion and verification
  - Not checking that the table was truly emptied rather than deleted — after deletion, verify the table still exists but contains zero rows

### Correct example (Java, JUnit style):
```java
// Insert two rows
tableOperations.create("testTable");
// (assuming BatchWriter writes two rows: row1 and row2)

// Delete all rows
tableOperations.deleteRows("testTable", null, null);

// Verify table is empty
Scanner scanner = connector.createScanner("testTable", Authorizations.EMPTY);
int count = 0;
for (Entry<Key,Value> entry : scanner) {
    count++;
}
assertEquals("Expected table to be empty after deleteRows(null, null)", 0, count);
```

### Incorrect example (what NOT to do):
```java
tableOperations.create("testTable");
// Only test with non-null boundaries
tableOperations.deleteRows("testTable", new Text("a"), new Text("z"));
// This misses the bug entirely because null-handling may be broken
```