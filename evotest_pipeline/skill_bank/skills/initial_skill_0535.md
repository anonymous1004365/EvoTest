---
name: query-result-set-comparison
description: When tests compare query results against resource files, verify that
  the resource file parsing correctly handles result lines and that set-based comparison
  tolerates different item orderings. A test may pass on one run but fail on another
  if results are compared as ordered instead of unordered sets.
code_tags:
- STATE_MUTATION
- NULL_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# query-result-set-comparison

## Instructions

# Query Result Set Comparison

## Instructions

- WHEN the TG is testing query execution (SQL2, XPath, etc.) and the test compares results against a resource file containing expected lines
- THEN the TG should verify that result comparison ignores ordering unless ordering is explicitly specified by the test. If the comparison uses ordered comparison (e.g., comparing line-by-line), reorder the expected results or change comparison to unordered (e.g., parse into a Set and compare sets).
- Include concrete values: expected results from the resource file, actual query results, and the set-based comparison method.
- Verify that resource file reading properly strips whitespace and handles blank lines (lines set as null/empty should not cause NPEs in comparison).
- Common pitfalls:
  - Comparing lists/arrays directly using ordered comparison when query results may arrive in a different order
  - Not reading/parsing the resource file correctly (e.g., missing last line, including blank lines as null values)
  - Using line-based comparison where the resource file's line count doesn't match the result set size causing AssertionError with different lengths
- When building the test for a buggy version, ensure the expected values from the resource file are converted to an unordered collection (Set) and the actual results are also converted, then assert equality on those sets.

### Correct Example

```java
// Correct: compare as unordered sets
Set<String> expected = new HashSet<>();
try (BufferedReader reader = new BufferedReader(
        new InputStreamReader(getClass().getResourceAsStream("expected.txt")))) {
    String line;
    while ((line = reader.readLine()) != null) {
        line = line.trim();
        if (!line.isEmpty()) {
            expected.add(line);
        }
    }
}
Set<String> actual = new HashSet<>(executeQuery("SELECT * FROM [nt:base]"));
assertEquals(expected, actual);
```

### Incorrect Example

```java
// Incorrect: ordered comparison may fail when results arrive in different order
List<String> expected = Files.readAllLines(Paths.get("expected.txt"));
List<String> actual = executeQuery("SELECT * FROM [nt:base]");
assertEquals(expected, actual);  // FAILS if ordering differs
```