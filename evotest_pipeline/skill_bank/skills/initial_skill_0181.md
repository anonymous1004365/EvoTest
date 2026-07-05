---
name: table-operations-throws-on-nonexistent-table
description: When implementing or testing TableOperations methods like setProperty,
  removeProperty, getProperties, listSplits, or checkIteratorConflicts on a mock or
  in-memory implementation, the TG should verify that calling these methods with a
  non-existent table name throws TableNotFoundException. The 'setProperties' (Map)
  variant must also be tested.
code_tags:
- ARGUMENT_VALIDATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# table-operations-throws-on-nonexistent-table

## Instructions

# Table Operations Must Throw TableNotFoundException for Non-Existent Tables

## Instructions

- WHEN testing methods on a `TableOperations` implementation (e.g., `MockTableOperations extends TableOperationsHelper`), especially methods like `setProperty`, `removeProperty`, `getProperties`, `listSplits`, `checkIteratorConflicts`, `getIteratorSetting`, `listIterators`, `removeIterator`, `attachIterator`, `setIteratorProperty`, `removeIteratorProperty`, or `getMaxRow`
- THEN the test MUST call each method with a table name string that does NOT exist (e.g., `"tableThatDoesNotExist"`), and verify that a `TableNotFoundException` (full class: `org.apache.accumulo.core.client.TableNotFoundException`) is thrown
- For `setProperties(Map<String,String>)`, pass a map of properties (e.g., `Collections.singletonMap("key", "value")`) with a non-existent table name
- For methods returning a value normally (e.g., `getProperties(String tableName)` returning `Iterable<Entry<String,String>>`), verify they throw the exception rather than returning an empty or null collection
- Test the following methods specifically:
  - `setProperty(tableName, property, value)` — throws `TableNotFoundException` for non-existent table
  - `removeProperty(tableName, property)` — throws `TableNotFoundException` for non-existent table
  - `getProperties(tableName)` — throws `TableNotFoundException` for non-existent table
  - `getMaxRow(tableName, ...)` — throws `TableNotFoundException` for non-existent table
  - `listSplits(tableName)` — throws `TableNotFoundException` for non-existent table
  - `getIteratorSetting(tableName, ...)` — throws `TableNotFoundException` for non-existent table
  - `listIterators(tableName)` — throws `TableNotFoundException` for non-existent table
  - `removeIterator(tableName, ...)` — throws `TableNotFoundException` for non-existent table
  - `attachIterator(tableName, ...)` — throws `TableNotFoundException` for non-existent table
  - `setIteratorProperty(tableName, ...)` — throws `TableNotFoundException` for non-existent table
  - `removeIteratorProperty(tableName, ...)` — throws `TableNotFoundException` for non-existent table
  - `checkIteratorConflicts(tableName, ...)` — throws `TableNotFoundException` for non-existent table
- Common pitfalls to avoid:
  - ❌ Testing only a few of these methods (e.g., testing only `setProperty` but not `getProperties`, `removeProperty`, `listSplits`, `getMaxRow`, or iterator-related methods) — the bug may be in any of them
  - ❌ Assuming that because a method returns a value (like `getProperties` returning `Iterable`), it won't throw; the contract requires `TableNotFoundException` for non-existent tables
  - ❌ Testing with an empty string or null instead of a non-existent table name — these may produce `IllegalArgumentException` or `NullPointerException`, which is a different error
  - ❌ Assuming the `setProperties(Map)` overload is covered by testing `setProperty(String, String, String)` — these are separate methods and must each be tested individually

### Correct Test Pattern (JUnit 4)
```java
@Test(expected = TableNotFoundException.class)
public void testGetPropertiesThrowsException() throws Exception {
    MockTableOperations ops = new MockTableOperations(...);
    ops.getProperties("tableThatDoesNotExist");
}
```

### Incorrect Test Pattern (would miss the bug)
```java
@Test
public void testGetPropertiesNoThrow() throws Exception {
    MockTableOperations ops = new MockTableOperations(...);
    // This would NOT catch the missing TableNotFoundException:
    Iterable<Entry<String,String>> props = ops.getProperties("tableThatDoesNotExist");
    assertNull(props);  // Bug: should have thrown, not returned null
}
```