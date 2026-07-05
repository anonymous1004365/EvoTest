---
name: validation-common-example-with-inherited-nodes
description: When testing query results with predefined JSON example trees, ensure
  both the root-level nodes AND the same-path nodes under the test's own tree are
  properly indexed before querying. Otherwise, index state from a parent test class
  may interfere with query results.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# validation-common-example-with-inherited-nodes

## Instructions

# Validation: Pre-Indexing Common Example Nodes in PropertyIndexQueryTest

## Instructions

WHEN the TG encounters a test that loads a predefined example tree (e.g., from "test" nodes defined in JSON via `loadTestContent`) and then runs an XPath or SQL2 query to verify results:

- THEN the TG MUST ensure that the `xpath.txt` (and `sql2.txt`) expected result files contain the **same basic root nodes** (e.g., `/test/a`, `/test/b`, `/test/c`) that the test class itself adds programmatically (e.g., via its own `createTestContent` method).
- The TG MUST also ensure that any **common example nodes** loaded by the test superclass (`AbstractQueryTest.loadTestContent`) are present in the expected output file, even if the test method adds additional or overlapping paths.
- WHEN `PropertyIndexQueryTest` calls `test("xpath.txt")`, the expected file must match the **combined** result of: (a) the common example from `loadTestContent`, (b) any extra content added by the test method itself.
- The TG MUST avoid assuming that the test only queries its own added content — the query may return results from inherited nodes that were already present in the repository before the test's own modifications.

### Common Pitfalls

1. **Assuming the test starts with an empty repository**: Tests may inherit state from `@Before` setup in the superclass (`AbstractQueryTest`). Always check what nodes are already present in the repository before running queries.
2. **Only including nodes added in the test method**: The expected `xpath.txt` must include nodes from `loadTestContent` (`/test`, `/test/a`, etc.) even though the test itself adds nodes like `/test/a/jcr:content`.
3. **Overlooking index state propagation**: The property index may have been built from previous test content. Queries return results from all indexed nodes, not just those added in the current test.

### Correct Example

For `PropertyIndexQueryTest.xpath()`:

```java
@Test
public void xpath() {
    // loadTestContent() adds /test, /test/a, /test/b, /test/c
    // This test adds /test/a/jcr:content with property "foo"
    // The query returns ALL matching nodes, including parent nodes from loadTestContent
    test("xpath.txt");  // expected output includes /test/a/jcr:content AND /test/a
}
```

Expected `xpath.txt` (excerpt):
```
/test/a/jcr:content
/test/a
/test/b
/test/c
...
```

### Incorrect Example

```java
@Test
public void xpath() {
    // WRONG: Assuming only the test's own content is returned
    test("xpath.txt");  // expected file only contains /test/a/jcr:content
}
```

Expected `xpath.txt` (WRONG — missing inherited nodes):
```
/test/a/jcr:content
<!-- Missing /test/a, /test/b, /test/c from loadTestContent! -->
```

### Key Verification

- Examine the `@Before` setup in the test class hierarchy to see what content is pre-loaded.
- Run the test against the **fixed** version to capture the full set of expected results.
- Ensure `xpath.txt`/`sql2.txt` files contain ALL matching nodes — from both inherited and test-specific content.