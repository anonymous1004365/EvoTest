---
name: resource-based-query-test-assertion
description: When tests run queries and compare results against resource files (e.g.,
  xpath.txt), ensure the test fails meaningfully when the query output differs from
  expected. This skill teaches how to detect broken query implementations via resource-based
  test assertions.
code_tags:
- XPATH_QUERY_TEST
- RESOURCE_BASED_ASSERTION
test_pattern: PARAMETRIC_TEST
---

# resource-based-query-test-assertion

## Instructions

# Resource-Based Query Test Assertion

## Instructions

- WHEN the TG encounters a test that executes XPath or SQL2 queries and compares results against a resource/expected output file (e.g., `src/test/resources/xpath.txt`)
- THEN the TG should verify that the expected output file is comprehensive enough to catch query result regressions. Specifically:
  1. The test should define a set of diverse query statements (XPath, SQL2) that exercise different query semantics: property equality, property range, path containment, node type constraints, ordering, etc.
  2. The expected output file should contain **both** query header lines (e.g., `## XPath query: ...`) **and** the corresponding result lines.
  3. The test framework (e.g., `AbstractQueryTest.test(String)`) loads the resource file, parses the queries and expectations, executes each query, and compares actual vs expected output line by line.
  4. A mismatch means the query engine produces wrong results — this is the critical signal that must be detected as a test failure.
  5. The test should include queries that probe the specific index or query feature being fixed (e.g., property index queries, path queries, node type queries).

- Common pitfalls to avoid:
  - Testing only one query type (e.g., only SQL2) when both XPath and SQL2 are supported.
  - Using overly simplistic expected data that doesn't exercise edge cases (e.g., missing nodes, ordering, multiple property conditions).
  - Writing tests that pass even when query results are wrong (e.g., by checking only count instead of full result set).
  - Not re-running the test after changes to the query engine — the resource file must be regenerated and compared.

### Correct example (as in this bug's test)

The test class `PropertyIndexQueryTest` extends `AbstractQueryTest` and calls `test("xpath.txt")`. The resource file `xpath.txt` contains:

```
## XPath query: //element(*, nt:base)[@x = 1]
/x
/y
...
```

The test framework in `AbstractQueryTest` reads this file, parses each query section, executes the query, and compares the output line-by-line with the expected results. If the property index implementation returns wrong results (e.g., missing nodes, extra nodes), the comparison fails.

### Incorrect example (pitfall)

```java
// WRONG: Only tests one query, no resource file comparison
@Test
public void testSimpleQuery() throws Exception {
    Iterator<ResultRow> results = executeQuery("//*[@x = 1]", "xpath");
    assertTrue(results.hasNext());  // Weak assertion — doesn't verify actual results
}
```

This would not catch the bug because the query might return *some* results but miss certain nodes, or return wrong nodes. The line-by-line resource comparison is essential.