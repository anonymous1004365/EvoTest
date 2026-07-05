---
name: query-result-file-comparison
description: When writing tests that compare query results against expected reference
  files, the TG should ensure the expected output file exists and is loaded correctly.
  This skill covers reading expected results from resource files, executing queries,
  and comparing outputs line-by-line.
code_tags:
- NULL_CHECK
- RESOURCE_MANAGEMENT
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# query-result-file-comparison

## Instructions

# Query Result File Comparison

## Instructions

- WHEN the TG encounters a test that loads expected query results from a resource file (e.g., `src/test/resources/.../xpath.txt`), a reference file containing expected query output lines
- THEN the TG should:
  1. **Load the reference file** from the test resources directory using `getClass().getResourceAsStream()` or `getResource()`, wrapped in a `BufferedReader` or `Scanner` inside a try-with-resources block
  2. **Read all expected lines** into a collection (e.g., `List<String>`) — trim each line and skip empty lines where appropriate
  3. **Execute the query** against the repository/index and collect result paths/strings into a comparable collection
  4. **Compare** the actual result lines to the expected result lines — typically using `assertEquals(expectedLines, actualLines)` for exact match, or iterate and compare each line
  5. **Close resources** properly — use try-with-resources for any `InputStream`, `BufferedReader`, or `Scanner` opened on resource files to avoid resource leaks

- WHEN the expected result file path is passed as a parameter to a helper method (e.g., `test("xpath.txt")`)
- THEN the TG should verify that:
  - The helper method constructs the full resource path correctly (e.g., `"/xpath.txt"` or relative to the test class package)
  - The resource file is found and readable (not null)
  - Each line from the expected output matches the corresponding actual result line

- Common pitfalls to avoid:
  - **Hardcoding absolute file paths** — always use `getResource()` / `getResourceAsStream()` so tests work across build systems
  - **Not closing the InputStream/BufferedReader** — always use try-with-resources or explicitly close in a finally block (RESOURCE_MANAGEMENT)
  - **Ignoring leading/trailing whitespace** when comparing lines — trim lines before comparison
  - **Assuming line ordering** when SQL results may not have a guaranteed order — use sorted collections or order-independent comparison if needed
  - **Using `File` or `FileInputStream`** instead of classpath resource loading — tests will fail when run from a JAR or different working directory

### Correct Example

```java
@Test
public void testQueryResults() throws Exception {
    // Load expected results from resource file
    List<String> expected;
    try (BufferedReader reader = new BufferedReader(
            new InputStreamReader(
                getClass().getResourceAsStream("/xpath.txt"), StandardCharsets.UTF_8))) {
        expected = reader.lines()
            .map(String::trim)
            .filter(line -> !line.isEmpty())
            .collect(Collectors.toList());
    }
    
    // Execute the query (e.g., XPath, SQL2)
    List<String> actual = executeQueryAndGetPaths("/jcr:root//element(*, nt:base)");
    
    // Compare
    assertEquals(expected, actual);
}
```

### Incorrect Example

```java
// BAD: Uses File with absolute/relative path — fails outside certain working directories
@Test
public void testQueryResults_bad() throws Exception {
    // File path is fragile
    List<String> lines = Files.readAllLines(
        Paths.get("src/test/resources/xpath.txt")); // WILL FAIL when run from different module
    
    // No try-with-resources — resource leak
    InputStream is = getClass().getResourceAsStream("/xpath.txt");
    BufferedReader reader = new BufferedReader(new InputStreamReader(is));
    // ... use reader but never close it
}
```