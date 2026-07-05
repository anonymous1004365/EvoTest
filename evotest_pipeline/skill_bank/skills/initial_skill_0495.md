---
name: partition-reorganize-null-safe-copy
description: WHEN the TG encounters DDL parsing code that copies a partition specification
  list, it should test that the parser correctly handles null/empty cases during reorganization
  operations where the parsed partition list may be null, preventing NullPointerException.
  This skill applies to any parser that processes ALTER TABLE ... REORGANIZE PARTITION
  statements.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# partition-reorganize-null-safe-copy

## Instructions

# Partition Reorganize Null-Safe Copy

## Instructions

- WHEN the TG encounters a DDL parser that handles `REORGANIZE PARTITION` statements and copies a list of partition specifications (e.g., `partitionSpecs` or similar field from a parsed statement object)
- THEN the TG should write a test that:
  1. Parses a `REORGANIZE PARTITION` DDL statement (e.g., `ALTER TABLE t REORGANIZE PARTITION p1 INTO (PARTITION p2 VALUES LESS THAN (10))`)
  2. Verifies that during the copy operation of partition specification lists, the parser does NOT throw a `NullPointerException`
  3. The test should specifically trigger the copy path that copies partition specs from one object to another — look for methods that iterate over `partitionSpecs` using `.forEach()` or a for-each loop directly on the list, without first checking if the list is null
  4. If the partition specifications list is `null` (e.g., because the REORGANIZE statement doesn't fill `partitionSpecs` the same way as a CREATE TABLE), the copy must handle this gracefully

- Common pitfalls to avoid:
  - Testing only `CREATE TABLE` partition parsing — the bug specifically manifests in `ALTER TABLE ... REORGANIZE PARTITION` where partition specs may remain null
  - Testing only `VALUES LESS THAN` bounds — the missing null check is on the partition specs list itself, not on individual partition bound values
  - Assuming that `partitionSpecs` is never null because it's set during `CREATE TABLE` — the bug is that the REORGANIZE code path doesn't populate it properly, and the copy code path doesn't guard against it

- Example of correct test:
```java
@Test
public void parsePartitionReorganize() {
    String ddl = "ALTER TABLE t REORGANIZE PARTITION p1 INTO (PARTITION p2 VALUES LESS THAN (10))";
    MySqlDdlParser parser = new MySqlDdlParser();
    // This should not throw NullPointerException when partitionSpecs is null
    parser.parse(ddl, tables);
    // Verify tables were parsed without error
    assertThat(tables.size()).isGreaterThan(0);
}
```

- Example of what would miss the bug (incorrect approach):
```java
// This only tests CREATE TABLE, not REORGANIZE PARTITION
@Test
public void testCreateTablePartition() {
    String ddl = "CREATE TABLE t (id INT) PARTITION BY RANGE (id) (PARTITION p1 VALUES LESS THAN (10))";
    // This works fine even in buggy version
    parser.parse(ddl, tables);
}
```