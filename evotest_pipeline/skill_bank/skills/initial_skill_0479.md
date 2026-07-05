---
name: empty-column-family-null-validation
description: When validating column family/qualifier pairs passed to input format
  configuration methods, ensure that null column families paired with non-null column
  qualifiers are not silently dropped. The TG should test with diverse combinations
  of null and non-null values to verify correct iteration and inclusion.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# empty-column-family-null-validation

## Instructions

# Empty Column Family Null Validation

## Instructions

- WHEN the TG encounters a method that accepts `Collection<Pair<Text,Text>>` representing column family/qualifier pairs for configuring an input format (e.g., `fetchColumns()` in `AccumuloInputFormat` or `InputFormatBase`)
- THEN the TG should test that when a `Pair<Text,Text>` has a **null column family** and a non-null column qualifier (e.g., `new Pair<Text,Text>(null, new Text("bar"))`), this entry is **NOT silently dropped** and appears correctly in the result set
  - Specifically: the test should verify that after configuring fetch columns with mixed entries — e.g., `[(foo,bar), (null,bar), (null,null), (foo,null), (null,bar)]` — all 5 entries are present in the stored columns
  - The expected set should NOT omit the `(null,bar)` entry; the buggy behavior drops the second `(null,"bar")` entry when iterating
- Common pitfalls to avoid:
  - **Testing only with non-null column families**: The bug only manifests when a null column family is paired with a non-null column qualifier. Testing only `(null, null)` or `(foo, bar)` combinations will NOT catch this bug.
  - **Assuming iteration order is deterministic**: The bug occurs because an iteration over duplicate-eliminated entries (e.g., stored in a `Set` or `Map` with null-sensitive operations) silently drops entries where the column family is null and the column qualifier is not null. Ensure the test checks for containment, not just order.
  - **Not covering edge cases**: Include all combinations: both non-null, both null, null family with non-null qualifier, non-null family with null qualifier, and duplicate entries.

### Correct example (would catch the bug):

```java
// This test catches the bug where (null, "bar") is dropped
@Test
public void testEmptyColumnFamily() throws IOException {
    // ... setup job ...
    Collection<Pair<Text,Text>> columnsToFetch = new ArrayList<>();
    columnsToFetch.add(new Pair<>(new Text("foo"), new Text("bar")));
    columnsToFetch.add(new Pair<>(null, new Text("bar")));   // null family, non-null qualifier
    columnsToFetch.add(new Pair<>(null, null));               // both null
    columnsToFetch.add(new Pair<>(new Text("foo"), null));    // non-null family, null qualifier
    columnsToFetch.add(new Pair<>(null, new Text("bar")));    // duplicate of above
    AccumuloInputFormat.fetchColumns(job, columnsToFetch);
    // ... verify all 5 entries are present ...
}
```

### Incorrect example (would miss the bug):

```java
// This test would PASS on the buggy version, missing the bug entirely
@Test
public void testColumnFamilies() throws IOException {
    Collection<Pair<Text,Text>> columnsToFetch = new ArrayList<>();
    columnsToFetch.add(new Pair<>(new Text("foo"), new Text("bar")));
    columnsToFetch.add(new Pair<>(new Text("foo"), null));
    columnsToFetch.add(new Pair<>(null, null));
    AccumuloInputFormat.fetchColumns(job, columnsToFetch);
    // All entries have either non-null family or both null — bug doesn't trigger
}
```