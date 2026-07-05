---
name: multi-not-equal-conjunction-handling
description: When a query contains multiple NOT EQUAL conditions on the same property
  combined with AND, the test generator should verify that the conjunction logic correctly
  filters nodes rather than incorrectly applying OR semantics. This skill applies
  to query engines and filter implementations with property restriction constraints.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# multi-not-equal-conjunction-handling

## Instructions

# Multi-NotEqual Conjunction Handling

## Instructions

- WHEN the TG encounters a query/filter evaluation path that handles `PropertyRestriction` objects with `isNot = true` (NOT EQUAL conditions containing property name, first/last values, and firstIncluding/lastIncluding flags)
- THEN the TG should write a test that:
  1. Creates multiple NOT EQUAL restrictions on the **same property** combined via AND logic
  2. Sets up test data containing nodes that match both conditions, only one condition, and neither condition
  3. Executes the query and asserts that only **both** conditions are satisfied simultaneously (not either/or)
  4. The expected result set size should be verified: with 2 matching nodes out of 3 total nodes, expect exactly 2 results (not 1 as the buggy version would produce)
  5. Uses the actual query mechanism (SQL2 or equivalent) to exercise the full filter chain

- WHEN writing the test, include these concrete elements:
  - Use the test framework's existing node creation utilities (e.g., `builder.child("n1").setProperty("prop", "val1")`)
  - Create at least 2 NOT EQUAL conditions: e.g., `prop <> 'value1' AND prop <> 'value2'`
  - Include at least 3 nodes where: node1 matches both exclusions, node2 matches one exclusion, node3 doesn't match either
  - The correct result should include nodes matching both conditions (e.g., value 'value3')
  - Assert on the result set size using the query execution result

- Common pitfalls to avoid:
  - Do NOT test NOT EQUAL conditions on different properties (the bug relates to same-property conjunction)
  - Do NOT test only a single NOT EQUAL condition (single conditions work correctly)
  - Do NOT assume AND between NOT EQUAL conditions on the same property behaves as OR
  - Do NOT test with OR instead of AND (the bug is specific to AND conjunction)
  - Do NOT rely on unit-testing filter logic in isolation; integration tests through the query engine are needed

- Example of correct test approach:
  ```java
  // Create test data
  builder.child("node1").setProperty("type", "type1")
         .child("node2").setProperty("type", "type2")
         .child("node3").setProperty("type", "type3");
  
  // Query: SELECT * FROM [nt:base] WHERE type <> 'type1' AND type <> 'type2'
  // Expected: only node3 matches (size=1)
  // Buggy version would also include node2, or incorrectly produce 0 results
  
  String sql2 = "SELECT * FROM [nt:base] AS t WHERE ISDESCENDANTNODE(t, '/test') " +
                "AND t.[type] <> 'type1' AND t.[type] <> 'type2'";
  Iterator<ResultRow> results = qe.executeQuery(sql2, SQL2, filter);
  assertEquals(1, Iterators.size(results));
  ```

- Example of incorrect test approach (would NOT catch the bug):
  ```java
  // Only tests a single NOT EQUAL - won't catch the multi-condition bug
  String sql = "SELECT * FROM [nt:base] AS t WHERE t.[type] <> 'type1'";
  ```