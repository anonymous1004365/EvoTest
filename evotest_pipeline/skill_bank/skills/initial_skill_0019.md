---
name: data-table-no-records-toolbar-initialization
description: When testing a DataTable that adds a NoRecordsToolbar (or similar conditional-visibility
  toolbar component), test that the toolbar does not throw unhandled exceptions during
  its onConfigure() method before the table has its data provider set up. This skill
  catches bugs where toolbar components try to access uninitialized state.
code_tags:
- TYPE_HIERARCHY_CHECK
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# data-table-no-records-toolbar-initialization

## Instructions

# DataTable NoRecordsToolbar Initialization Exception Detection

## Instructions

- WHEN the TG encounters a `DataTable` subclass that adds a toolbar component (e.g., `NoRecordsToolbar`) during construction, and that toolbar's `onConfigure()` method depends on the data provider being attached
- THEN the TG should test that constructing the `DataTable` with no items/rows and rendering it does NOT throw an `IndexOutOfBoundsException` (or any unhandled `RuntimeException`) during `onConfigure()` of the toolbar
- Specifically, test with an empty data provider (zero rows), create the `DataTable` with columns, add the `NoRecordsToolbar` (or equivalent), and call `renderHead()` or trigger rendering on the table. The buggy version throws an exception because `NoRecordsToolbar.onConfigure()` accesses an index or state that hasn't been initialized yet
- Verify that the exception is caught and handled properly, OR that the toolbar's `onConfigure()` checks for null/uninitialized state before accessing it
- Common pitfalls:
  - Testing only with non-empty data providers, missing the edge case where the table has zero rows
  - Not testing the rendering lifecycle (i.e., only testing construction), since the bug manifests during `onConfigure()` which is called during the render phase
  - Assuming that the toolbar's `onConfigure()` is independent of the data table's internal state

### Example (correct test - catches the bug):

```java
// Test that DataTable with NoRecordsToolbar and empty data does not throw
@Test
public void testWicket3603()
{
    // Create DataTable with 0 rows
    IDataProvider<Object> emptyProvider = new EmptyDataProvider();
    DataTable<Object, String> table = new DataTable<>("table", columns, emptyProvider, 10);
    // Add the NoRecordsToolbar - buggy version throws during render
    table.addTopToolbar(new NoRecordsToolbar(table));
    
    // This should not throw IndexOutOfBoundsException
    table.renderHead();  // or equivalent rendering call
}
```

### Example (incorrect test - misses the bug):

```java
// BAD: Only tests construction, doesn't trigger rendering lifecycle
@Test
public void testDataTableCreation()
{
    DataTable<Object, String> table = new DataTable<>("table", columns, provider, 10);
    table.addTopToolbar(new NoRecordsToolbar(table));
    // No rendering call - won't catch the onConfigure() bug
}
```