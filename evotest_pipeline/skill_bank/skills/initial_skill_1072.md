---
name: mysql-antlr-default-value-parsing
description: When parsing default values from SQL statements using ANTLR parsers,
  test that time-related default value expressions (like '00:00:00') are correctly
  parsed and do not produce exceptions. This skill helps detect parsing errors for
  time literal expressions in MySQL connector default value handling.
code_tags:
- ARGUMENT_VALIDATION
- ARRAY_INDEX_ACCESS
- BOUNDARY_CHECK
- STATE_MUTATION
- TYPE_CONVERSION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# mysql-antlr-default-value-parsing

## Instructions

# MySQL ANTLR Default Value Time Parsing

## Instructions

- WHEN the TG encounters code that parses MySQL column default values from SQL CREATE TABLE statements using ANTLR grammar rules (e.g., parsing expressions like `DEFAULT '00:00:00'` for TIME columns)
- THEN the TG should write a test that:
  1. Creates a table with a TIME column that has a default value expressed as a string literal time expression (e.g., `DEFAULT '00:00:00'`)
  2. Parses the CREATE TABLE statement using the MySQL ANTLR parser (e.g., `MysqlAntlrDefaultValueParser`)
  3. Verifies that parsing the default value does NOT throw an exception
  4. Verifies that the parsed default value object is non-null and correctly represents the expected default value
- Common pitfalls to avoid:
  - Testing only with DATE or TIMESTAMP default values but not TIME column defaults, which have different parsing paths
  - Assuming string literal time expressions like `'00:00:00'` are handled identically to other temporal literal expressions
  - Not testing edge cases like midnight (`'00:00:00'`), full time (`'23:59:59'`), or zero time (`'00:00:00'`)

### Example (correct test)

```java
@Test
public void parseTimeDefaultValue() {
    String sql = "CREATE TABLE test (id INT, t TIME DEFAULT '00:00:00')";
    MySqlParser parser = new MySqlParser(sql);
    // Should parse without exception
    parser.parse();
    DefaultValue value = parser.getDefaultValue("t");
    assertNotNull(value);
    // Expected value depending on representation (e.g., "00:00:00")
}
```

### Example (incorrect test — insufficient coverage)

```java
// BAD: Only tests DATE default values, misses the TIME path entirely
@Test
public void parseDateDefaultValue() {
    String sql = "CREATE TABLE test (id INT, d DATE DEFAULT '2020-01-01')";
    // ... only tests DATE, not TIME
}
```