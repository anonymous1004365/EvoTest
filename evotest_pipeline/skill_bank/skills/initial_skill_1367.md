---
name: column-name-reserved-word-parsing
description: When DDL parser logic processes SQL statements where column names are
  also SQL reserved words (e.g., a column named 'column'), the parser may incorrectly
  consume the column name as part of the SQL syntax. This skill teaches how to test
  parsing of column names that match SQL reserved keywords.
code_tags:
- VALIDATION
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# column-name-reserved-word-parsing

## Instructions

# Column Name Reserved Word Parsing

## Instructions

- WHEN the TG encounters DDL parsing logic that extracts column names from SQL `ALTER TABLE` or `CREATE TABLE` statements, and those column names could coincide with SQL reserved words (e.g., `column`, `table`, `index`, `primary`, `foreign`, `key`, `not`, `null`, `default`, `auto_increment`, `comment`, `after`),
- THEN the TG should write a parametric test that verifies parsing of SQL statements where column names match reserved words. For each reserved word used as a column name, the test must:
  1. Construct a DDL statement such as `ALTER TABLE t1 ADD COLUMN <reserved_word> INT;` or `ALTER TABLE t1 CHANGE COLUMN existing_col <reserved_word> INT;`
  2. Parse the statement through the DDL parser
  3. Assert that the parsed column name equals the reserved word (e.g., `"column"`, `"table"`, `"index"`)
  4. Assert that the parsed SQL statement is not null and does not throw a parse exception
  5. Verify that no columns with other names are accidentally included (e.g., no phantom `"COLUMN"` string token consumed as a column name)

- Concrete example for the method under test: when an `ALTER TABLE ... ADD COLUMN column INT;` statement is parsed, the parser must produce a column named `"column"` of type `INT`, not drop the word `column` as syntax noise.

- Common pitfalls to avoid:
  - Testing only column names that are NOT reserved words (e.g., `foo`, `bar`, `my_column`). This misses the bug entirely.
  - Forgetting to test both `ADD COLUMN` and `CHANGE COLUMN` / `MODIFY COLUMN` variants.
  - Assuming the DDL parser handles the ambiguity of a column name matching a keyword token (e.g., assuming the parser's grammar already accounts for the keyword being used as an identifier).
  - Not checking the returned column name's equality — a parse that succeeds but produces an incorrect column name (e.g., `null`, `""`, or a different string) must be detected.
  - Testing only one reserved word; multiple reserved words commonly appear in column name position (e.g., `column`, `table`, `index`, `order`, `group`, `select`, `from`, `where`).

- Correct test style (Java/JUnit): use `@ParameterizedTest` with `@ValueSource(strings = {"column", "table", "index", "order", "group", "primary"})` or `@CsvSource`, parse the DDL, and assert on the parsed column name and type.

- Incorrect test style: writing a single test with `ALTER TABLE t1 ADD COLUMN my_col INT;` which would pass even with the buggy parser, because `my_col` is not a reserved word.