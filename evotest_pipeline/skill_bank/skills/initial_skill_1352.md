---
name: deep-copy-state-preservation
description: When a class overrides deepCopy() and has mutable fields (Matcher, Charset,
  etc.) that maintain internal state, the copy must create independent instances of
  those fields — otherwise the original and copy share mutable state, leading to test
  failures after copy operations.
code_tags:
- VALIDATION
- DEEP_COPY_STATE
test_pattern: STATE_TEST
---

# deep-copy-state-preservation

## Instructions

# Deep Copy State Preservation

## Instructions

- WHEN the Test Generator (TG) encounters a class that implements a `deepCopy(IteratorEnvironment)` method and contains mutable state fields such as `Matcher` (from `java.util.regex`), `Charset`, or other mutable objects
- THEN the TG should write a test that:
  1. Creates an instance of the class with specific state (e.g., regex patterns set via `init()` or `setRegexs()`)
  2. Configures the instance so it processes some data and advances its internal `Matcher` state (e.g., calls `seek()` then `next()` to advance position)
  3. Calls `deepCopy()` on the instance with a `DefaultIteratorEnvironment`
  4. Verifies that operations on the copy do NOT affect the original's state and vice versa — they must behave as independent objects
- Use `org.apache.accumulo.core.iterators.DefaultIteratorEnvironment` for the environment parameter when calling `deepCopy()`
- Verify that after `deepCopy()`, both the original and the copy produce correct results independently when iterating through data

**Common pitfalls to avoid:**
- Testing only that `deepCopy()` compiles or returns a non-null value — the TG must verify behavioral independence of the copy.
- Assuming that `Matcher` objects are inherently immutable — `Matcher` instances hold internal position state (via `reset()`, `find()`, `matches()`) and must be re-derived from the `Pattern` to get independent copies.
- Not re-initializing the iterator after deepCopy — the copy may need `seek()` before use, but the independence of state should be verifiable even if the copy is used differently.
- Forgetting that `orFields` and `matchSubstring` boolean fields must also be copied independently (the buggy `copyMatcher()` method correctly re-creates matchers from patterns, but the test should still verify the full state preservation).

**Correct example (verifies independent state after deepCopy):**
```java
// Setup data
TreeMap<Key,Value> tm = new TreeMap<>();
newKeyValue(tm, "boo1", "yup", "20080201", "dog");
newKeyValue(tm, "boo1", "yap", "20080202", "cat");
newKeyValue(tm, "boo2", "yip", "20080203", "hamster");

// Create and configure filter
RegExFilter rei = new RegExFilter();
IteratorSetting is = new IteratorSetting(1, RegExFilter.class);
RegExFilter.setRegexs(is, "boo1", null, null, null, false);
rei.init(new SortedMapIterator(tm), is.getOptions(), new DefaultIteratorEnvironment());
rei.seek(new Range(), EMPTY_COL_FAMS, false);

// Advance original state
assertTrue(rei.hasTop());
rei.next(); // move past first match

// Deep copy
RegExFilter copy = (RegExFilter) rei.deepCopy(new DefaultIteratorEnvironment());
// Copy must also call seek()
copy.seek(new Range(), EMPTY_COL_FAMS, false);

// Both should still produce correct, independent results
assertTrue(copy.hasTop());
assertTrue(rei.hasTop());
```

**Incorrect example (state not verified):**
```java
// Just testing deepCopy doesn't crash — insufficient!
RegExFilter copy = (RegExFilter) rei.deepCopy(new DefaultIteratorEnvironment());
assertNotNull(copy); // This doesn't verify independent state
```