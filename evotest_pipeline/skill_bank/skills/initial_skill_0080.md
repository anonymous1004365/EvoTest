---
name: query-index-result-validation
description: When implementing or modifying index-based query tests that compare results
  against expected files, the TG should ensure changes to query behavior or data seeding
  are reflected in both the expected output files and the test assertions. This skill
  prevents mismatches between actual query results and expected baseline files.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# query-index-result-validation

## Instructions

# Query Index Result Validation

## Instructions

- WHEN the TG encounters a test that executes queries against an index (e.g., `PropertyIndexQueryTest.sql2Index()`) and compares the results against an expected resource file (e.g., `sql2_index.txt`)
- THEN the TG should verify that any modifications to the data seeding (e.g., `AbstractQueryTest` setup/teardown) or query behavior correctly produce the expected output in the comparison file. Specifically:
  - Check that the expected resource file (`src/test/resources/sql2_index.txt`) is updated to match the new actual query output when test data or query construction logic changes
  - The test typically uses `test("sql2_index.txt")` or similar methods that load expected results from a resource file and compare them with actual query execution results
  - Verify that the test's resource file reflects the current state of the test data seeder and the query under test

- WHEN the TG sees a query test that compares results to a `.txt` resource file
- THEN the TG should include the expected resource file in the test setup, ensuring it exists at the correct path and contains the exact lines that the query will produce (including ordering). Common pitfalls:
  - Modifying test data (trees/nodes added, removed, or modified) without updating the expected output file
  - Changing query construction (e.g., SQL-2 syntax, predicate conditions, or result ordering) without updating the expected output file
  - Adding new test methods that share a resource file without accounting for the cumulative effect

- Example of correct approach:
```java
// Test class: PropertyIndexQueryTest
// Method: sql2Index
// This test reads from src/test/resources/sql2_index.txt and compares
// against actual query results. If you modify setup() to add test data,
// you MUST also update sql2_index.txt with the new expected output.
@Test
public void sql2Index() {
    test("sql2_index.txt");
}
```

- Example of incorrect approach (BUGGY):
```java
// Modifying AbstractQueryTest setup to add new test data without
// updating sql2_index.txt causes test failure because actual results
// (which now include the new data) don't match the old expected output.
// The fix requires updating BOTH the test code and the resource file.
```

- WHEN the TG writes a test that validates query index results against expected output files
- THEN the TG should ensure the test data carefully controls what gets indexed and queried, AND that the expected output file contains exactly what the query returns. Mistakes to avoid:
  - Not regenerating the expected output file after changing query predicates, sorting, or projection
  - Assuming the expected output file is correct without verifying line-by-line correspondence
  - Forgetting that resource files are loaded from the classpath at `src/test/resources/<test-class-simple-name>/` or similar relative path