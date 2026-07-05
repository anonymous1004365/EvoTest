---
name: empty-index-query-boundary
description: When testing property index queries with empty/null indexes, ensure SQL2
  queries that filter on indexed properties are executed and validated for correct
  behavior, catching boundary issues where an empty index set causes query errors
  or unexpected results.
code_tags:
- CONDITIONAL_BRANCH
- RESOURCE_MANAGEMENT
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# empty-index-query-boundary

## Instructions

# Empty Index Query Boundary Testing

## Instructions

- WHEN the TG encounters a property index test that executes SQL2 queries (e.g., `SELECT * FROM [nt:base] WHERE [property] = 'value'`) and the test method calls `test("sql2.txt")` to execute queries from a resource file
- THEN the TG should:
  1. Verify that the test resource file (`sql2.txt`) contains queries that exercise indexed properties
  2. Ensure the test creates a proper property index via a method like `createPropertyIndex(String propertyName)` before executing queries
  3. Test with BOTH populated data (where indexed properties have meaningful values) AND edge cases such as:
     - Empty/null property values in nodes
     - Missing indexed nodes entirely (no nodes that match)
     - Multiple nodes with the same indexed property value
  4. Verify correctness by comparing actual query results against expected results loaded from query result files (e.g., `sql2.txt.txt`), confirming the number of expected rows and values match
  5. Catch bugs where an empty or malformed index causes the query to return wrong results, throw unexpected exceptions, or behave differently than expected

- Common pitfalls to avoid:
  - Testing only with data that always produces non-empty query results, missing empty-result edge cases
  - Not verifying both the count AND the content of query results (just checking non-null is insufficient)
  - Assuming property index setup is sufficient without testing queries that actually filter on indexed properties
  - Forgetting to test with multiple query statements in the same resource file

- Correct example:
```java
// Test with data that produces results AND with empty/missing data
@Test
public void sql2() throws Exception {
    test("sql2.txt");  // resource contains queries like SELECT * FROM [nt:base] WHERE [jcr:title] = 'foo'
}

// The test resource creates appropriate property indexes:
// createPropertyIndex("jcr:title")
// and inserts nodes BOTH with and without the indexed property
```

- Incorrect example:
```java
// Too narrow: only testing with data that always produces non-empty results
// and not verifying that empty index scenarios don't cause errors
@Test
public void sql2() throws Exception {
    test("sql2.txt");  // but the resource file has insufficient edge case queries
}
```