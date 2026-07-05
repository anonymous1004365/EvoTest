---
name: sql2-query-roundtrip-parity
description: When testing SQL query parsers that support multi-language query formats
  (e.g., SQL-2 and XPath), the test must verify that parsing and re-serialization
  of complex queries (e.g., UNION queries with wildcard properties like [*/size])
  produces correct roundtrip output without truncation or parser confusion.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# sql2-query-roundtrip-parity

## Instructions

# SQL2 Query Roundtrip Parser Parity

## Instructions

- WHEN the TG encounters a SQL query parser that supports both SQL-2 syntax and XPath-to-SQL2 conversion, and the parser is tested by parsing a string and re-serializing it back to a string for comparison
- THEN the TG should verify roundtrip parity by:
  1. Writing a test that parses a query string and then calls `.toString()` (or equivalent) on the parsed result
  2. Asserting that the output string equals the input string
  3. Including UNION queries with complex predicates (e.g., wildcard property selectors like `[*/size]`, `[*/*/size]`, `[*/*/*/size]`, `[*/*/*/*/size]`, `[*/*/*/*/*/size]`)
  4. Including the corresponding XPath representation of the same query to verify that the SQL-2 → XPath → SQL-2 roundtrip is lossless
  5. Expecting a `ParseException` on the buggy version if the parser incorrectly handles the query
- Common pitfalls to avoid:
  - Testing only single-statement queries without UNION or multi-clause queries
  - Testing only simple property predicates (e.g., `[size]`) without wildcard path variants (e.g., `[*/size]`, `[/*/size]`)
  - Testing only the SQL-2 parse path without also testing the XPath-to-SQL2 conversion and back
  - Relying on the parser to silently truncate or skip malformed wildcard expressions rather than throwing a `ParseException`
  - Assuming that if one wildcard level works (e.g., `[*/size]`), deeper levels (e.g., `[*/*/size]`, `[*/*/*/*/*/size]`) also work

### Correct Example
```java
@Test
public void testRoundtripWithWildcardUnions() throws ParseException {
    String query = "select [jcr:path], [jcr:score], * from [nt:base] as a " +
        "where isdescendantnode(a, '/etc/commerce/products') " +
        "and [cq:commerceType] = 'product' and [size] = 'M' " +
        "union select [jcr:path], [jcr:score], * from [nt:base] as a " +
        "where isdescendantnode(a, '/etc/commerce/products') " +
        "and [cq:commerceType] = 'product' and [*/size] = 'M'";
    Query q = p.parseQuery(query);
    String result = q.toString();
    assertEquals(query, result);
}
```

### Incorrect Example
```java
// Only tests simple single-statement query without UNION or wildcard properties
@Test
public void testSimpleQuery() throws ParseException {
    String query = "select * from [nt:base] as a where [size] = 'M'";
    Query q = p.parseQuery(query);
    assertEquals(query, q.toString()); // Passes trivially, misses the bug
}
```