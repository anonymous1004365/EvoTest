---
name: seek-before-has-top-check
description: When facing an iterator pattern, the TG must test that performing seek()
  before calling hasTop() on a source iterator does not cause a NullPointerException.
  This is a common pitfall in Accumulo-style iterators where the source may not have
  been initialized yet.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# seek-before-has-top-check

## Instructions

# Seek Before HasTop: NullPointerException in Iterator Patterns

## Instructions

- WHEN the TG encounters an iterator class that uses a source iterator (e.g., `docSource`, `source`, `child`) and calls methods like `getTopKey()`, `getTopValue()`, or `getTopKey().toString()` on that source
- THEN the TG should write a test that:
  1. Creates an instance of the iterator under test (e.g., `FamilyIntersectingIterator`)
  2. Sets up the iterator options (e.g., via `IteratorSetting` with column family/index options)
  3. Calls `.init(source, options, iteratorEnvironment)` to initialize the iterator
  4. Calls `.seek(range, columnFamilies, inclusive)` on the iterator **without** first calling `hasTop()` on the source
  5. **Verifies that no NullPointerException is thrown** — or that the behavior is correctly handled

- **Common pitfall**: The TG might assume that `seek()` on the outer iterator is only called after the source iterator has already been advanced. But the bug occurs when `seek()` leads to code that calls `docSource.getTopKey().toString()` or similar before `docSource.hasTop()` is checked. The fix pattern is to check `docSource.hasTop()` before calling `docSource.getTopKey()`.

- **Concrete values**: For `FamilyIntersectingIterator`, the test should:
  - Create columns like `colFam` and `colQual` for document and index
  - Set up `IteratorSetting` with `docColumn` option
  - Call `init()` with a `SortedMap`-based source iterator
  - Call `seek()` with a `Range` (e.g., the whole range or a specific row range)
  - **Expect**: No exception. Previously, the buggy version threw a `NullPointerException` because `docSource.hasTop()` was not checked before `docSource.getTopKey().toString()`.

### Example (correct test approach):

```java
// Setup
IteratorSetting iterSetting = new IteratorSetting(1, FamilyIntersectingIterator.class);
iterSetting.addOption(IndexedDocIterator.DOC_COL_OPT, ...);
// ... other options

FamilyIntersectingIterator iter = new FamilyIntersectingIterator();
iter.init(new SortedMapIterator(someData), iterSetting.getOptions(), env);
iter.seek(new Range(), Collections.emptyList(), false);
// No NullPointerException should occur
```

### Example (pitfall — testing only after advancing source):

```java
// WRONG: This only tests happy path where source already has data
source.seek(range, cols, inclusive);
source.next(); // advances source
// Then test outer iterator
iter.seek(range, cols, inclusive);
// This might pass on buggy code because source is already advanced
```