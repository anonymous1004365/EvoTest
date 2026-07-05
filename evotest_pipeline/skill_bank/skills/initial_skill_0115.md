---
name: data-table-column-sorting-stability
description: When testing DataTable with initial sort state, verify that setting a
  sort order does not cause a NullPointerException due to uninitialized internal state.
  Test that column-sorted state transitions correctly handle default unsorted columns.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# data-table-column-sorting-stability

## Instructions

# DataTable Column Sorting State Initialization

## Instructions

- WHEN the TG encounters a DataTable construction that involves setting an initial sort order (e.g., `new DataTable(...)` with an `ISortState` parameter that specifies a column index with an initial sort property)
- THEN the TG should test with a DataTable that has a column with **no initial sort order** (i.e., the column appears in the table but the `ISortState` does not specify any sort property for that column index, or uses `null`/empty for the sort property), and verify that calling `getSortState().setSortOrder(columnIndex, SortOrder.ASCENDING)` does **not** throw a `NullPointerException` or any other exception
- The TG should verify that when a column's sort order is set and then the sort state is retrieved, the internal sort state map (of `SortState` within `DataTable`) correctly finds the column's `ISortStateLimiter` without a NullPointerException during the lookup
- Include what mistakes to avoid: **common pitfall** — testing only with columns that have a pre-initialized sort property; failing to test with columns whose sort property is `null` or empty in the sort state, which can trigger a `NullPointerException` in the internal `SortState.getSortOrder()` logic when the column index is not yet tracked in the internal sort state map

### Correct test approach (example)
```java
DataTable<?, ?> table = new DataTable<>("table", columns, dataProvider, rowsPerPage);
ISortState sortState = table.getSortState();
// Set sort order on a column index that has no prior sort property
sortState.setSortOrder(0, SortOrder.ASCENDING);
// Verify no exception thrown and the sort order is correct
assertEquals(SortOrder.ASCENDING, sortState.getSortOrder(0));
```

### Incorrect test approach (common pitfall)
```java
// Only testing with columns that already have a sort property set
// This misses the bug when the column index has no sort property
ISortState sortState = table.getSortState();
// Fails to test setSortOrder(columnIdx, SortOrder.ASCENDING) where
// columnIdx has no existing sort property in the state map
```