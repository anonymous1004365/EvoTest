---
name: combiner-sumall-columns-test
description: When testing Combiner subclasses like SummingCombiner that use the `all`
  option to combine across all columns, ensure the test uses a non-null column family
  qualifier so the column set check matches. Without this, columns are skipped and
  values are not combined.
code_tags:
- STATE_MUTATION
- COLLECTION_ITERATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# combiner-sumall-columns-test

## Instructions

# Combiner `sumAllColumns` Test Methodology

## Instructions

- WHEN the TG tests a Combiner implementation (e.g., `SummingCombiner`) configured with the `setCombineAllColumns(is, true)` option (i.e., `IteratorSetting` with `"all"` option set to `"true"`), AND the input data contains multiple Key-Value pairs with the same row/column family/column qualifier/visibility but different timestamps:
  - THEN the test MUST verify that the combiner's `reduce()` method is called correctly and the combined top value equals the expected aggregated result.
  - Use `Combiner.setCombineAllColumns(is, true)` rather than `Combiner.setColumns(is, list)` to ensure all columns are combined.
  - Ensure the test data uses a non-null column family AND column qualifier that do NOT match any special filtering (e.g., avoid using an empty string `""` or a column family value of `"2"` as the first argument to `newKeyValue` — instead use the same column family prefix format as other tests, like `"cf001"`).
  - The `SummingCombiner` should combine values for keys that differ only by timestamp. For example, with values 2, 3, 4 at timestamps 1, 2, 3, the combined value should be `"9"` (2+3+4) when `reduceOnFullCompactionOnly` is false (default) and the iterator scope is `scan`.
  - Assert that after `seek(new Range(), ...)`, the top key's value decodes to the summed total (e.g., `9` for inputs 2, 3, 4 with `VarLenEncoder`).
  - Assert that after `next()`, `hasTop()` returns `false` (all combined entries consumed).
  - **Avoid this mistake**: Do NOT use column family `"2"` (e.g., `newKeyValue(tm1, 1, 1, 1, 1, false, 2l, encoder)` with a column qualifier of `"1"` and expecting aggregation). Column `"2"` as a column family will NOT be matched by the `all` option test because it is a numeric string column family, and the combiner's matching logic may filter it out. Always use the same column family/qualifier format as the aggregation target — e.g., family `"cf001"`, qualifier `"cq001"`.

- Correct example:
  ```java
  TreeMap<Key,Value> tm1 = new TreeMap<>();
  newKeyValue(tm1, 1, 1, 1, 1, false, 2l, encoder);
  newKeyValue(tm1, 1, 1, 1, 2, false, 3l, encoder);
  newKeyValue(tm1, 1, 1, 1, 3, false, 4l, encoder);

  Combined ai = new SummingCombiner();
  IteratorSetting is = new IteratorSetting(1, SummingCombiner.class);
  LongCombiner.setEncodingType(is, VarLenEncoder.class);
  Combiner.setCombineAllColumns(is, true);
  ai.init(new SortedMapIterator(tm1), is.getOptions(), SCAN_IE);
  ai.seek(new Range(), EMPTY_COL_FAMS, false);

  assertTrue(ai.hasTop());
  assertEquals(newKey(1, 1, 1, 3), ai.getTopKey());
  assertEquals("9", encoder.decode(ai.getTopValue().get()).toString());
  ai.next();
  assertFalse(ai.hasTop());
  ```

- Incorrect example (bug-triggering pattern):
  ```java
  TreeMap<Key,Value> tm1 = new TreeMap<>();
  newKeyValue(tm1, 1, 1, 1, 1, false, 2l, encoder);
  newKeyValue(tm1, 1, 1, 1, 2, false, 3l, encoder);
  newKeyValue(tm1, 1, 1, 1, 3, false, 4l, encoder);

  Combined ai = new SummingCombiner();
  IteratorSetting is = new IteratorSetting(1, SummingCombiner.class);
  LongCombiner.setEncodingType(is, VarLenEncoder.class);
  Combiner.setCombineAllColumns(is, true);
  ai.init(new SortedMapIterator(tm1), is.getOptions(), SCAN_IE);
  ai.seek(new Range(), EMPTY_COL_FAMS, false);

  // BUG: the test incorrectly expects the summed result "9" but gets "4"
  // because the combiner did NOT actually combine — it passes through individual values.
  // The issue is the column family/qualifier mismatch or the `all` option not being picked up.
  // On the buggy version, test fails with: expected:<[9]> but was:<[4]>
  assertEquals("9", encoder.decode(ai.getTopValue().get()).toString()); // FAILS
  ```