---
name: accumulo-input-format-range-validation
description: When configuring Accumulo InputFormatBase subclasses, the TG should validate
  that configuring a null or empty range throws an IllegalArgumentException or is
  properly handled. Covers both mapred and mapreduce API variants.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# accumulo-input-format-range-validation

## Instructions

# Accumulo InputFormat Range Validation

## Instructions

WHEN the TG encounters code that sets input ranges, iterators, or configuration on an Accumulo `InputFormatBase` subclass (e.g., `AccumuloRowInputFormat`, `AccumuloInputFormat`, `AccumuloMultiTableInputFormat` in both `mapred` and `mapreduce` packages):

- THEN the TG should test that calling `setRanges()` with a **null** or **empty** collection of `Range` objects produces an `IllegalArgumentException` (or `IOException`) in both `mapred` and `mapreduce` API variants.
- THEN the TG should test that setting an invalid or null `IteratorSetting` via `addIterator()` or `addScanIterator()` throws an appropriate exception.
- THEN the TG should verify that setting **no ranges at all** (default state) causes the job to either fail predictably or use sensible defaults (e.g., scanning the entire table).
- THEN include explicit test methods that:
  1. Set ranges to `Collections.emptyList()` and expect failure.
  2. Set ranges to `null` directly and expect failure.
  3. Verify the exception message or type matches `IllegalArgumentException.class` or `IOException.class`.
- THEN for the `mapreduce` API, use `InputFormatBase` from `org.apache.accumulo.core.client.mapreduce` package. For `mapred`, use `org.apache.accumulo.core.client.mapred` package.
- THEN the test should be structured as a unit test (not an integration test requiring a running Accumulo instance), using mocks or a test configuration helper to set up the job configuration.

**Common pitfalls to avoid:**
- ❌ Testing only the `mapreduce` variant but not the `mapred` variant (or vice versa). Both packages have similar bugs.
- ❌ Only testing with a non-null but incorrect range, while forgetting to test the null case explicitly.
- ❌ Assuming the default (no ranges set) will work — verify the expected behavior explicitly.
- ❌ Writing only integration tests (IT) that require a cluster; write a focused unit test that catches the input validation bug.
- ❌ Testing only one method (e.g., `setRanges()`) while neglecting related configuration methods like `addIterator()` or `fetchColumns()`.

### Correct Example

```java
// In mapreduce package
@Test(expected = IllegalArgumentException.class)
public void testSetRangesThrowsOnNull() throws IOException {
  Job job = Job.getInstance();
  AccumuloInputFormat inputFormat = new AccumuloInputFormat();
  // Simulating: user forgets to set ranges or sets null
  AccumuloInputFormat.setRanges(job, null);
  // The buggy version would not throw / would silently accept null
}

@Test(expected = IllegalArgumentException.class)
public void testSetRangesThrowsOnEmpty() throws IOException {
  Job job = Job.getInstance();
  AccumuloInputFormat.setRanges(job, Collections.emptyList());
}
```

### Incorrect Example (does not catch the bug)

```java
// ❌ Only tests with valid ranges — misses null/empty validation gap
@Test
public void testSetRangesValid() throws IOException {
  Job job = Job.getInstance();
  ArrayList<Range> ranges = new ArrayList<>();
  ranges.add(new Range("a", "z"));
  AccumuloInputFormat.setRanges(job, ranges);
  // No exception thrown — but this doesn't validate error handling!
}

// ❌ Only checks mapreduce, not mapred
// ❌ Never tests null or empty input
```