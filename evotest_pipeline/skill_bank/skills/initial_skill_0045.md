---
name: table-id-map-consistency
description: When testing methods that return a map of table names to IDs from a mock
  or in-memory implementation, verify that operations like table creation, deletion,
  and renaming keep the map in sync. Also test that tableIdMap() returns the correct
  mapping after table creation.
code_tags:
- STATE_MUTATION
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# table-id-map-consistency

## Instructions

# Table ID Map Consistency

## Instructions

- WHEN the TG encounters a method named `tableIdMap()` that returns a `Map<String,String>` mapping table names to table IDs
- THEN the TG should test that:
  1. Calling `tableIdMap()` immediately after creating a table returns a map containing the new table name with a **non-null, non-empty, valid** table ID string
  2. The table ID should be a newly generated ID, not equal to the table name itself or to IDs of other tables
  3. The map correctly reflects the current set of tables (created tables appear, deleted tables disappear)
- Include a test that creates a table, calls `tableIdMap()`, and asserts that:
  - The returned map contains the table name as a key
  - The value (table ID) is not null and not empty
  - The table ID is different from the table name (e.g., assertNotEquals(tableName, tableIdMap.get(tableName)))
- Common pitfalls:
  - Testing only that `tableIdMap().containsKey(tableName)` returns true, without verifying the actual ID value
  - Assuming the table ID equals the table name or some predictable string
  - Not checking that table creation actually populates the map at all
- Correct example:
  ```java
  String tableName = "testTable";
  tableOps.create(tableName);
  Map<String,String> idMap = tableOps.tableIdMap();
  assertTrue(idMap.containsKey(tableName));
  String tableId = idMap.get(tableName);
  assertNotNull(tableId);
  assertFalse(tableId.isEmpty());
  assertNotEquals(tableName, tableId);
  ```
- Incorrect example (would pass even with the bug):
  ```java
  String tableName = "testTable";
  tableOps.create(tableName);
  // Only checks key existence, not the value
  assertTrue(tableOps.tableIdMap().containsKey(tableName));
  ```