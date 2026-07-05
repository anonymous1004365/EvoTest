---
name: mock-table-versioning-iterator-config-mismatch
description: WHEN creating mock tables with NewTableConfiguration, verify that the
  withoutDefaultIterators() flag is correctly propagated through to the MockTable
  constructor. The `limitVersion` boolean in NewTableConfiguration controls whether
  default versioning iterators are applied, and this state must match between the
  configuration and the actual MockTable instantiation.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# mock-table-versioning-iterator-config-mismatch

## Instructions

# Mock Table Versioning Iterator Configuration Propagation

## Instructions

WHEN the test involves creating tables in the mock Accumulo framework using `NewTableConfiguration` (especially calling `withoutDefaultIterators()` or relying on the default versioning behavior), THEN the test should verify that the number of entries written matches expectations based on whether versioning iterators are active or not.

- WHEN testing with `new NewTableConfiguration().withoutDefaultIterators().setTimeType(TimeType.LOGICAL)`, THEN write 3 entries with the same row/cf/cq but different timestamps, THEN verify that all 3 entries are readable (expected count = 3).
- WHEN testing with `new NewTableConfiguration().setTimeType(TimeType.MILLIS)` (default, with versioning), THEN write 3 entries with the same row/cf/cq but different timestamps, THEN verify that only 1 entry is readable (expected count = 1) because the VersioningIterator is active.
- AFTER attaching a `VersioningIterator` (at priority 20) to a table created without default iterators, THEN re-verify that only 1 entry remains readable.
- WHEN testing that attaching a VersioningIterator to a table created with MILLIS time type and default versioning, THEN verify that attaching the iterator fails with `AccumuloException`.
- WHEN writing test data, use `BatchWriter` and `Mutation` with the same row, column family, and column qualifier but different values (e.g., `String.valueOf(i)` for i = 0, 1, 2) in separate `BatchWriter` sessions to ensure timestamps differ.
- WHEN asserting results, use `BatchScanner` with `Range.exact("row1", "cf", "cq")` and count the number of entries returned.

Common pitfalls to avoid:
- Testing only the table creation without actually writing and reading data to verify versioning behavior.
- Assuming the same behavior for LOGICAL and MILLIS time types — they handle versioning differently (LOGICAL allows multiple versions, MILLIS creates unique timestamps via System.currentTimeMillis() but still version-reduces).
- Forgetting to close the BatchWriter before writing the next mutation — each mutation must be in its own writer session to get different timestamps.
- Not testing the `withoutDefaultIterators()` flow separately from the default versioning flow — both paths must be tested independently.
- Failing to test that attaching a VersioningIterator to a table already having versioning (MILLIS + default) throws an exception.

### Correct Example:
```java
// Test without default iterators: expect all 3 entries
conn.tableOperations().create(t, new NewTableConfiguration().withoutDefaultIterators().setTimeType(TimeType.LOGICAL));
writeVersionable(conn, t, 3);
assertVersionable(conn, t, 3); // Should be 3

// Attach VersioningIterator
IteratorSetting settings = new IteratorSetting(20, VersioningIterator.class);
conn.tableOperations().attachIterator(t, settings);
assertVersionable(conn, t, 1); // Now only 1
```

### Incorrect Example (buggy behavior):
```java
// Creates table but generatesInitialTableProperties(limitVersion=false)
// but then MockAccumulo.createTable(username, tableName, TimeType, Map)
// creates MockTable without the limitVersion boolean constructor
// Result: versioning is ON despite withoutDefaultIterators() being called
conn.tableOperations().create(t, new NewTableConfiguration().withoutDefaultIterators().setTimeType(TimeType.LOGICAL));
// Bug: only 1 entry is readable instead of 3
```