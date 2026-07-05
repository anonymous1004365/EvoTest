---
name: regex-filter-accept-null-field-behavior
description: Use this skill when testing Filter subclasses whose accept() method passes
  potentially null field data (row/column/qualifier) to a matches() helper. The TG
  should verify the filter behaves correctly when some fields have regex matchers
  while others do not, especially regarding the default return value when a matcher
  is null.
code_tags:
- FILTER_ACCEPT_BEHAVIOR
test_pattern: STATE_TEST
---

# regex-filter-accept-null-field-behavior

## Instructions

# RegExFilter Accept Behavior with Null Matchers

## Instructions

- WHEN the TG encounters a `Filter` subclass (like `RegExFilter`) whose `accept(Key, Value)` method passes `ByteSequence` data from `key.getRowData()`, `key.getColumnFamilyData()`, `key.getColumnQualifierData()` to a private `matches(Matcher, ByteSequence)` helper, and the `matches` helper returns `!orFields` when the matcher is null
- THEN the TG must test that when ONLY SOME fields have regex matchers set (others are null), the `accept()` method correctly includes/excludes entries according to:
  - In **AND mode** (`orFields=false`): if a matcher is null on one field, that field's check returns `true` (since `!orFields` = `!false` = `true`), so only non-null matchers need to match — the TG should verify that entries matching all non-null regexes pass, and entries failing any non-null regex are rejected
  - In **OR mode** (`orFields=true`): if a matcher is null on one field, that field's check returns `false` (since `!orFields` = `!true` = `false`), so only fields with non-null matchers can contribute to the OR — the TG should verify that an entry matching ANY non-null regex passes, and entries matching NO non-null regex are rejected
- The TG should construct a test with at least 3 entries having distinct row/cf/cq values, set regexes on only some dimensions (e.g., only row regex, leave cf/cq/value null), then verify the correct entries pass through using `rei.hasTop()` and `rei.getTopKey().equals(expectedKey)`
- A common pitfall is testing with ALL four regexes set (row, cf, cq, value) which doesn't exercise the null matcher logic — the TG must test with some regexes explicitly left null to verify the `!orFields` return path
- Example correct test pattern:
  ```java
  TreeMap<Key,Value> tm = new TreeMap<>();
  Key k1 = newKeyValue(tm, "boo1", "yup", "20080201", "dog");
  Key k2 = newKeyValue(tm, "boo1", "yap", "20080202", "cat");
  Key k3 = newKeyValue(tm, "boo2", "yip", "20080203", "hamster");

  RegExFilter rei = new RegExFilter();
  IteratorSetting is = new IteratorSetting(1, RegExFilter.class);
  RegExFilter.setRegexs(is, ".*2", null, null, null, false);  // only row regex, cf/cq/value null

  rei.init(new SortedMapIterator(tm), is.getOptions(), new DefaultIteratorEnvironment());
  rei.seek(new Range(), EMPTY_COL_FAMS, false);

  assertTrue(rei.hasTop());
  assertEquals(k3, rei.getTopKey());  // only boo2 matches .*2
  rei.next();
  assertFalse(rei.hasTop());
  ```
- Incorrect test pattern (doesn't exercise null matcher path):
  ```java
  RegExFilter.setRegexs(is, "boo1", "yap", "20080202", "cat", false);  // all fields set
  ```