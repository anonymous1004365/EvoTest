---
name: alter-table-add-constraint-unique-parsing
description: When parsing SQL ALTER TABLE statements that add a CONSTRAINT ... UNIQUE
  KEY clause, the parser may fail to properly track its state across the CONSTRAINT
  keyword. This skill teaches how to write tests that catch SQL DDL parsing errors
  for ALTER TABLE ADD CONSTRAINT UNIQUE KEY patterns.
code_tags:
- VALIDATION
- STATE_MUTATION
- PARSER_STATE_TRACKING
test_pattern: EXCEPTION_TEST
---

# alter-table-add-constraint-unique-parsing

## Instructions

# SQL DDL Parser State Tracking for ALTER TABLE ADD CONSTRAINT UNIQUE KEY

## Instructions

- WHEN the TG encounters a SQL DDL parser that processes `ALTER TABLE ... ADD CONSTRAINT ... UNIQUE KEY (...)` statements (or similar ALTER TABLE ADD CONSTRAINT patterns where a keyword like `UNIQUE KEY` follows `CONSTRAINT`)
- THEN the TG should write a test that:
  1. Constructs a full SQL DDL statement string containing the relevant syntax (e.g., `ALTER TABLE t1 ADD CONSTRAINT uq1 UNIQUE KEY (col1)`)
  2. Feeds it to the parser's `parse()` method (or equivalent entry point)
  3. Verifies that the parser produces the correct parsed representation — for example, by checking that the resulting data structure contains the expected `CREATE TABLE` definition including the unique key constraint
  4. If the parser has a separate "parsed result" object (e.g., table schema, constraint list, DDL statement list), assert that the constraint appears with the correct type, name, and columns
- Common mistakes to avoid:
  - Testing only `ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY` without also testing `UNIQUE KEY` or `PRIMARY KEY` — the constraint keyword parsing may work for one subtype but fail for others
  - Assuming that parsing a single `KEY (col)` clause (without `CONSTRAINT name`) works the same as the `CONSTRAINT name KEY (...)` form — the parser may handle state differently when a `CONSTRAINT` identifier precedes the keyword
  - Not checking the final parsed data structure (e.g., list of constraints) — the parse may complete without exception but silently drop the constraint
- Correct example:
  ```java
  @Test
  public void shouldParseAlterTableAddConstraintUniqueKey() {
      String ddl = "ALTER TABLE t1 ADD CONSTRAINT uq1 UNIQUE KEY (col1)";
      List<DdlParserListener.DataFrameEvent> events = parser.parse(ddl, tables);
      // Verify that the resulting table has a unique constraint named "uq1" on column "col1"
      Table table = tables.forTable(new TableId(null, null, "t1"));
      assertThat(table.constraintType("uq1")).isEqualTo(Table.ConstraintType.UNIQUE);
      assertThat(table.constraintColumns("uq1")).containsExactly("col1");
  }
  ```
- Incorrect example (too narrow):
  ```java
  @Test
  public void shouldParseAlterTableAddConstraintUniqueKey() {
      // Only tests the simple "KEY(col)" form without CONSTRAINT name — misses the bug
      String ddl = "ALTER TABLE t1 ADD UNIQUE KEY (col1)";
      parser.parse(ddl, tables);
      // No assertions on the parsed result — silently passes even if constraint is dropped
  }
  ```