---
name: mysql-ddl-grammar-type-resolution
description: When writing tests for DDL parsers that use ANTLR grammar to parse SQL
  statements with type modifiers like precision/scale or display width/decimals, the
  TG should test that type attributes parsed from string tokens are correctly converted
  from their raw string forms to numeric values using appropriate parsing mechanisms
  (e.g., Integer.parseInt), not defaulting to zero on failure. This skill helps catch
  bugs where missing or incorrectly resolved type attributes silently produce zero
  values instead of expected defaults or parsed values.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# mysql-ddl-grammar-type-resolution

## Instructions

# MySQL DDL Parser Type Attribute Resolution

## Instructions

WHEN the TG encounters code that parses DDL (Data Definition Language) SQL statements — especially type definitions with numeric modifiers such as precision/scale for DECIMAL/NUMERIC types or display width/decimals for fixed-point types — THEN the TG should:

1. **Test the parsing of SQL type definitions that include numeric type attributes** (e.g., `DECIMAL(10,2)`, `DECIMAL(20)`, `FIXED(8,3)`) and verify the parsed precision/scale values are correctly extracted.

2. **Use a DDL parser test framework** that can feed SQL strings to the parser and inspect the resulting column definitions. The test should verify that:
   - The `precision()` value of the parsed column matches the expected integer from the SQL
   - The `scale()` value of the parsed column matches the expected integer from the SQL
   - The numeric attribute methods (like `precision()` and `scale()`) return the correct parsed values, not zero or some other default

3. **Test edge cases where:**
   - Type has both precision and scale specified: `DECIMAL(10,2)` → precision=10, scale=2
   - Type has only precision specified: `DECIMAL(20)` → precision=20, scale should NOT unexpectedly change
   - Type with no modifiers: `DECIMAL` → should handle gracefully (fallback to default behavior)

4. **Verify the state of DataTypeSchema or column metadata objects** after parsing — specifically check that `precision()` and `scale()` (or equivalent accessor methods on the column type) return expected values consistent with the SQL definition.

5. **Avoid the common pitfall** of only parsing DECIMAL types without checking which state/method returns the parsed attribute value. The bug may involve returning the raw string token directly instead of converting it via `Integer.parseInt()` or similar numeric conversion — which returns 0 on failure instead of throwing or handling properly.

### Correct Test Example (pseudocode):
```java
@Test
public void testDecimalPrecisionScaleParsing() {
    // Given a DDL statement with decimal types having precision and scale
    String ddl = "CREATE TABLE test (col1 DECIMAL(10,2), col2 DECIMAL(20), col3 DECIMAL);";
    parser.parse(ddl);
    Table table = parser.getTable("test");
    
    // col1: DECIMAL(10,2)
    assertThat(table.column("col1").type().precision()).isEqualTo(10);
    assertThat(table.column("col1").type().scale()).isEqualTo(2);
    
    // col2: DECIMAL(20) - scale should not affect precision or be misinterpreted
    assertThat(table.column("col2").type().precision()).isEqualTo(20);
    
    // col3: DECIMAL - no modifiers, should handle gracefully
    // (verify it doesn't crash or produce invalid negative/zero)
}
```

### Incorrect Test Example (common pitfalls):
```java
// BAD: Only tests DECIMAL types without checking the actual precision/scale values
@Test
public void testDecimalParsing() {
    String ddl = "CREATE TABLE test (col1 DECIMAL(10,2), col2 DECIMAL, col3 FIXED(8,3));";
    parser.parse(ddl);
    // Missing: assertion on precision() and scale() values
    // The test may pass even if these return 0 (incorrectly)
}
```