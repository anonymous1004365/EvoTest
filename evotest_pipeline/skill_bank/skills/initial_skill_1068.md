---
name: xpath-query-resource-mismatch-detection
description: When testing XPath query engines with expected results loaded from resource
  files, ensure the test compares the exact query output against the expected result
  file. Verify that queries producing wrong results (due to index or query engine
  bugs) are caught by mismatches between actual results and expected lines.
code_tags:
- NULL_CHECK
- VALIDATION
- RESOURCE_MANAGEMENT
test_pattern: PARAMETRIC_TEST
---

# xpath-query-resource-mismatch-detection

## Instructions

# XPath Query Result Validation Against Resource Files

## Instructions

- WHEN the TG encounters a query engine test that loads expected results from a resource file (e.g., `xpath.txt`) and runs queries through a `test()` method
- THEN the TG should ensure that the test method:
  1. Loads the resource file containing XPath queries and their expected SQL2 conversions or result sets
  2. For each query in the resource file, executes it against the query engine
  3. Compares the actual output (rows returned) against the expected output line by line
  4. If outputs don't match, reports a test failure with detailed diff information

- Verify that the test loads the resource file using `getClass().getResourceAsStream(...)` or similar classpath resource loading, NOT hardcoded file paths
- Verify that the test iterates through all queries in the resource file — do NOT assume only a subset is relevant
- Verify that the test checks for ordering of results when the query uses `ORDER BY` — output must be compared in exact order
- Common pitfalls:
  - ❌ Testing only one hand-picked XPath query instead of all queries from the resource file
  - ❌ Hardcoding expected results instead of loading them from the resource file
  - ❌ Ignoring row ordering in the comparison when `ORDER BY` is present
  - ❌ Not diffing actual vs expected output clearly enough to detect subtle mismatches
  
- Correct approach example:
  ```java
  @Test
  public void xpath() throws Exception {
      test("xpath.txt");  // Loads all queries from resource and compares output
  }
  ```
  Where the `test()` method reads the resource file, parses queries, executes them, collects results, and diffs against expected lines.

- Wrong approach example:
  ```java
  @Test
  public void testXPathQuery() {
      String xpath = "/jcr:root//element(*, oak:Unstructured)[@foo]";
      String sql2 = convert(xpath);
      assertEquals("SELECT * FROM [oak:Unstructured] WHERE [foo] IS NOT NULL", sql2);
      // Only tests one query, doesn't use the resource file at all
  }
  ```

- Expect that a buggy index or query engine may produce wrong results for some queries in the resource file while passing others — the resource-file-driven test approach catches these regressions by comparing full output.