---
name: filter-deleted-key-skipping
description: When implementing or testing a Filter that iterates over SortedKeyValueIterator
  sources, the findTop() method must skip deleted keys (isDeleted() == true) by calling
  source.next(). The bug occurs when findTop() skips deleted keys only when the accept()/negate
  condition is met, but fails to advance past deleted keys that happen to be accepted.
  Tests should verify that deleted keys are always skipped regardless of the accept()
  outcome.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- DELETED_KEY_FILTERING
test_pattern: STATE_TEST
---

# filter-deleted-key-skipping

## Instructions

# Filter Deleted Key Skipping

## Instructions

- WHEN the TG encounters a `Filter` class that extends `WrappingIterator` and overrides `findTop()` to iterate through source entries using `accept(Key, Value)` and a `negate` flag
- THEN the TG should write a test where:
  1. The source iterator contains entries where `getTopKey().isDeleted()` returns `true`
  2. The filter's `accept()` method returns `true` for those deleted entries (i.e., the accept logic does NOT check `isDeleted()`)
  3. The test verifies that `filter.seek()` followed by iteration using `hasTop()`/`next()` correctly skips the deleted entries — the deleted entries should NOT appear in the output
  4. The test must assert the count of non-deleted entries returned, NOT just verify that no exception is thrown

- The root cause of the bug is in `findTop()`:
  ```java
  // Buggy behavior:
  while (source.hasTop() && !source.getTopKey().isDeleted() 
         && (negate == accept(source.getTopKey(), source.getTopValue()))) {
      source.next();
  }
  ```
  The condition `!source.getTopKey().isDeleted()` is part of the `while` guard. This means when a deleted key is encountered **and** `(negate == accept(...))` evaluates to `false` (i.e., the filter would accept the key), the loop exits early and the deleted key is returned as `hasTop() = true`. The fix moves the deleted key check inside the loop body so it is always advanced past.

- Common pitfalls to avoid:
  - ❌ Testing only with non-deleted keys — this misses the bug entirely
  - ❌ Testing deleted keys that `accept()` returns `false` for — the bug only manifests when `accept()` returns `true` for deleted keys
  - ❌ Testing `negate=true` with deleted keys that `accept()` returns `false` for — same bug manifests because `negate == false` (accept returns false, negate=true, so `negate == accept` = `true == false` = `false`, loop exits)
  - ❌ Assuming the `Filter` base class correctly handles deleted keys — the bug shows it does not when accept matches

- ✅ Correct test approach (using a filter that accepts all keys):
  ```java
  // Filter that accepts everything — accept() returns true unconditionally
  public static class AcceptAllFilter extends Filter {
      @Override
      public boolean accept(Key k, Value v) {
          return true;  // This triggers the bug: deleted keys pass accept() but are NOT skipped
      }
  }
  
  @Test
  public void testFilterSkipsDeletedKeys() throws IOException {
      TreeMap<Key,Value> data = new TreeMap<>();
      Key k1 = new Key(new Text("row1"), new Text("cf"), new Text("cq"));
      k1.setDeleted(true);  // Marked as deleted
      data.put(k1, new Value("deleted".getBytes()));
      
      Key k2 = new Key(new Text("row2"), new Text("cf"), new Text("cq"));
      // k2 is NOT deleted
      data.put(k2, new Value("live".getBytes()));
      
      AcceptAllFilter filter = new AcceptAllFilter();
      filter.init(new SortedMapIterator(data), EMPTY_OPTS, null);
      filter.seek(new Range(), EMPTY_COL_FAMS, false);
      
      int count = 0;
      while (filter.hasTop()) {
          count++;
          filter.next();
      }
      // Only the non-deleted entry should be returned
      assertEquals("Deleted key was not skipped by filter", 1, count);
  }
  ```

- ❌ Incorrect test approach (misses the bug):
  ```java
  // Test only checks non-deleted keys — will pass on both buggy and fixed code
  @Test
  public void testFilterNormalKeys() throws IOException {
      // ... only non-deleted keys in data
      // Will pass on both versions
  }
  ```

- The key insight: test the **interaction** between `isDeleted()` and `accept()`. Create a filter whose `accept()` returns `true` for all entries (or specifically for the deleted ones), then verify that deleted entries are still skipped.