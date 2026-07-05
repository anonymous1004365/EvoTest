---
name: mock-table-operations-exception-handling
description: WHEN testing mock implementations of table operations (like MockTableOperations)
  that throw TableNotFoundException, THEN write tests that verify the exception is
  thrown for nonexistent tables. This skill helps detect missing or broken exception
  handling in mock/simulated table operations.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- CONCURRENCY
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# mock-table-operations-exception-handling

## Instructions

# Mock Table Operations Exception Handling

## Instructions

- WHEN the TG encounters a mock or simulated implementation of table operations (e.g., `MockTableOperations`) that has methods throwing `TableNotFoundException` for nonexistent tables
- THEN it should write a test that:
  1. Creates a mock connector and obtains the `TableOperations` instance
  2. Calls methods like `getProperties(String tableName)` on a table name that does NOT exist (e.g., `"table1"`)
  3. Expects the call to throw a `TableNotFoundException`
  4. Does NOT rely on the `tableList()` or similar methods to first verify the table exists

- Common pitfalls to avoid:
  - ❌ Calling `tableOps.exists("table1")` before the exception test — the `exists()` check itself might be broken
  - ❌ Only testing with valid/created tables instead of nonexistent ones
  - ❌ Forgetting to declare `throws TableNotFoundException` in the mock helper class's `getProperties()` override

- **Correct example** (what the TG should produce):
  ```java
  @Test(expected = TableNotFoundException.class)
  public void testTableNotFoundForGetProperties() throws Exception {
      Connector connector = new MockConnector();
      TableOperations tops = connector.tableOperations();
      tops.getProperties("nonexistentTable");
  }
  ```

- **Incorrect example** (what the TG should avoid):
  ```java
  @Test
  public void testTableNotFoundForGetProperties() throws Exception {
      Connector connector = new MockConnector();
      TableOperations tops = connector.tableOperations();
      // Buggy: doesn't assert the exception at all
      tops.getProperties("nonexistentTable");
  }
  ```