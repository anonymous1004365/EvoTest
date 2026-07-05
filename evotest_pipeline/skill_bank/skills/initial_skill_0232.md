---
name: mock-batch-scanner-thread-results
description: When testing a mock BatchScanner where separate threads scan different
  ranges and merge results, the test generator must verify that results from all threads
  are properly collected. This skill teaches how to catch bugs where thread results
  silently vanish without errors.
code_tags:
- EDGE_CASE_INPUT
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# mock-batch-scanner-thread-results

## Instructions

# Mock BatchScanner Thread Result Collection Test

## Instructions

- WHEN the TG encounters a `MockBatchScanner` (or any mock/scoped BatchScanner) that uses multiple threads to scan separate ranges (e.g., via `scan(Key, Key)` or `setRanges(List<Range>)`) and the results are collected from an `Iterator<Entry<Key,Value>>`:
  - THEN the TG should write a state test that:
    1. Inserts multiple rows (e.g., keys "a", "b", "c", "d") into a table
    2. Creates ranges that should each match one or more rows (e.g., range "a" to "d" inclusive)
    3. Uses the `BatchScanner` to scan those ranges
    4. Collects all results from the scanner's iterator
    5. Asserts that ALL expected rows are present in the result (e.g., `assertEquals(4, results.size())` or `assertEquals(expectedSet, resultSet)`)
  - Common pitfalls to avoid:
    - Testing with only a single thread (which won't trigger the concurrency/merge bug)
    - Testing with only a single range (the bug may manifest only when multiple ranges produce disjoint results)
    - Assuming `count()` or `hasNext()` returning true means all results are present
    - Not checking the actual content/keys of returned entries (the bug returns zero rows instead of the expected rows)
  - Correct example (detects the bug):
    ```java
    // Create table and insert rows with keys "a", "b", "c", "d"
    // Create BatchScanner with multiple ranges covering these keys
    BatchScanner bs = connector.createBatchScanner(...);
    bs.setRanges(Collections.singletonList(new Range("a", "d")));
    Set<String> keys = new HashSet<>();
    for (Entry<Key,Value> entry : bs) {
        keys.add(entry.getKey().getRow().toString());
    }
    bs.close();
    assertEquals(new HashSet<>(Arrays.asList("a", "b", "c", "d")), keys);
    ```
  - Incorrect example (does NOT detect the bug):
    ```java
    bs.setRanges(Collections.singletonList(new Range("a")));
    int count = 0;
    for (Entry<Key,Value> entry : bs) count++;
    assertTrue(count > 0);  // May pass on buggy version if single range works
    ```