---
name: complex-boolean-or-query-results
description: ''
code_tags:
- EMPTY_INDEX_HANDLING
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# complex-boolean-or-query-results

## Instructions

# Complex Boolean OR Query Result Counting

## Instructions

- WHEN the TG encounters code that evaluates boolean OR queries with multiple indexed properties (e.g., `(prop1 = X OR prop2 = Y) AND (prop3 = Z OR prop4 = W)`),
  THEN it should test that the result set size matches expectations for all valid combinations of property values.

- Specifically, if the code involves combining multiple sub-queries via OR/AND logic on a Lucene property index (e.g., `oak: LucenePropertyIndex`), 
  THEN the TG should explicitly assert the exact count of results returned (e.g., `assertEquals(2, resultSet.size())`), 
  not just that results are non-empty or that certain nodes are present.

- WHEN testing complex OR queries (with 3+ terms or nesting),
  THEN the TG should use a query like `//*[(prop1 = 'valA' or prop1 = 'valB') and (prop2 = 'valC' or prop2 = 'valD')]` 
  and verify that the exact number of matching nodes matches manual expectation, 
  since the index planner may return nodes that only partially satisfy the query (i.e., returning extra false positives).

- Common pitfalls to avoid:
  - Testing only single-condition OR queries (e.g., `prop = X OR prop = Y`)
  - Asserting only that certain nodes appear in the result set without checking total count
  - Using vague assertions like `assertTrue(result.size() > 0)` instead of exact `assertEquals(expected, result.size())`
  - Not testing the case where overlapping nodes could be counted twice by the query planner

**Correct approach (catches this bug):**
```java
// Setup: create nodes with properties such that a complex OR/AND query
// should return exactly 2 results but the bug causes 3
String query = "//*[(prop1 = 'a' or prop1 = 'b') and (prop2 = 'c' or prop2 = 'd')]";
List<String> result = query(query, SQL2);
// Verify exact count, not just non-empty
assertEquals("Result set size is different", 2, result.size());
assertTrue(result.contains("node1"));
assertTrue(result.contains("node2"));
```

**Wrong approach (would miss the bug):**
```java
// Only checks that specific results are present, not total count
List<String> result = query(query, SQL2);
assertTrue(result.contains("node1"));  // Wrong: doesn't catch extra results
assertTrue(result.contains("node2"));
```