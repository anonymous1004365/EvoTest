---
name: visibility-label-parsing-failure-recovery
description: When validating entries with visibility labels in Accumulo iterators,
  the VisibilityFilter catches parsing exceptions (VisibilityParseException, BadArgumentException)
  and falls back to filtering out entries silently. Use this skill when testing code
  that creates ColumnVisibility objects from raw user-supplied visibility label bytes.
code_tags:
- VALIDATION
- EXCEPTION_HANDLING
- FILTER_ACCEPT_BEHAVIOR
test_pattern: STATE_TEST
---

# visibility-label-parsing-failure-recovery

## Instructions

# Visibility Label Parsing Failure Recovery

## Instructions

- WHEN the TG encounters code that creates a `ColumnVisibility` object from raw byte arrays (like `new ColumnVisibility(testVis.toArray())`) inside a try-catch block that catches `VisibilityParseException` or `BadArgumentException` and logs an error before returning `false`
- THEN the TG MUST write a test that provides malformed/invalid visibility label data (e.g., `"A&"` which is an incomplete expression with a dangling operator) to verify that:
  1. The invalid visibility entry does not cause an unhandled exception to propagate
  2. The invalid entry is filtered out (e.g., `assertFalse(filter.hasTop())` after seeking)
  3. The iterator continues to function correctly for subsequent entries
- Include a concrete example: create a `TreeMap<Key,Value>` with a `Key` whose visibility label is `"A&"` (a malformed expression), wrap it with `VisibilityFilter.wrap(...)`, seek the iterator, and assert that no entry is returned (the bad visibility entry is silently skipped)
- Common pitfalls to avoid:
  - Testing only with well-formed visibility expressions (e.g., `"A"`, `"A|B"`) — this misses the parsing failure recovery path
  - Forgetting to suppress logging (set `Logger.getLogger(VisibilityFilter.class).setLevel(Level.FATAL)`) if the test environment might produce distracting error log output
  - Assuming that a `VisibilityParseException` or `BadArgumentException` will propagate as a test failure — these exceptions are caught and swallowed inside the `accept()` method

## Example

**Correct test (catches the bug):**
```java
public void testBadVisibility() throws IOException {
  TreeMap<Key,Value> tm = new TreeMap<>();
  // "A&" is an incomplete visibility expression — dangling operator
  tm.put(new Key("r1", "cf1", "cq1", "A&"), new Value(new byte[0]));
  SortedKeyValueIterator<Key,Value> filter = VisibilityFilter.wrap(
      new SortedMapIterator(tm), new Authorizations("A"), "".getBytes());

  // suppress logging noise
  Level prevLevel = Logger.getLogger(VisibilityFilter.class).getLevel();
  Logger.getLogger(VisibilityFilter.class).setLevel(Level.FATAL);

  filter.seek(new Range(), new HashSet<ByteSequence>(), false);
  assertFalse("Bad visibility entry should be filtered out", filter.hasTop());

  Logger.getLogger(VisibilityFilter.class).setLevel(prevLevel);
}
```

**Incorrect test (misses the bug):**
```java
public void testBadVisibility() throws IOException {
  TreeMap<Key,Value> tm = new TreeMap<>();
  // Testing with a valid visibility label — will NOT exercise the error path
  tm.put(new Key("r1", "cf1", "cq1", "A"), new Value(new byte[0]));
  SortedKeyValueIterator<Key,Value> filter = VisibilityFilter.wrap(
      new SortedMapIterator(tm), new Authorizations("A"), "".getBytes());

  filter.seek(new Range(), new HashSet<ByteSequence>(), false);
  assertTrue(filter.hasTop());
}
```

**Another pitfall — assuming exception propagation:**
```java
// WRONG — this test would fail because the exception is caught,
// not thrown; the entry is simply filtered out
@Test(expected = VisibilityParseException.class)
public void testBadVisibilityWrong() throws IOException {
  // ...
  filter.seek(new Range(), new HashSet<ByteSequence>(), false);
  // No exception is thrown — VisibilityParseException is caught inside accept()
}
```