---
name: filter-accept-deleted-key-handling
description: When testing Filter subclasses, verify that the accept(Key, Value) method
  correctly handles keys marked as deleted (isDeleted()=true) — deleted keys should
  not be counted as accepted entries, and the filter should correctly distinguish
  between regular entries and deleted tombstones.
code_tags:
- FILTER_ACCEPT_BEHAVIOR
- STATE_MUTATION
test_pattern: STATE_TEST
---

# filter-accept-deleted-key-handling

## Instructions

# Filter Accept Behavior for Deleted Keys

## Instructions

- WHEN a Filter subclass's `accept(Key, Value)` method is being tested — for example, a filter that counts accepted entries or applies criteria to keys
- THEN the test MUST include a case where the Key's `isDeleted()` flag is `true`, and verify that the filter does NOT count the deleted key as an accepted entry, or that the filter handles deleted keys differently from regular keys
- Specifically, construct a `Key` with the `isDeleted` parameter set to `true` (e.g., `new Key(row, cf, cq, cv, timestamp, true, false)`) and assert that the filter's `accept()` method returns `false` for it, or that the counting logic does not increment for it
- Also verify the opposite case — a Key with `isDeleted=false` (normal entry) IS accepted and counted correctly
- Common pitfalls to avoid:
  - Testing only with normal (non-deleted) Key entries and never constructing Keys with `isDeleted=true`
  - Assuming that the `isDeleted` flag is irrelevant to filtering logic — in Accumulo, deleted keys are tombstones and should generally not be counted as accepted
  - Using `Key` constructors that default `isDeleted` to `false` without explicitly testing the `true` case
  - For age-off / TTL filters: deleted keys should typically be passed through (accepted) rather than aged off, since they represent deletion tombstones

### Correct Example (Java)
```java
// Test that a counter filter does NOT count deleted keys
Key deletedKey = new Key("row".getBytes(), "cf".getBytes(), "cq".getBytes(),
    "cv".getBytes(), 100L, true, false);  // isDeleted=true
Value v = new Value("val".getBytes());
assertFalse(filter.accept(deletedKey, v));

// Test that a normal key IS counted
Key normalKey = new Key("row".getBytes(), "cf".getBytes(), "cq".getBytes(),
    "cv".getBytes(), 100L, false, false);  // isDeleted=false
assertTrue(filter.accept(normalKey, v));
```

### Incorrect Example (Java)
```java
// BUG: Only tests with default isDeleted=false, never tests deleted flag
Key key = new Key("row", "cf", "cq", "cv", 100L);
Value v = new Value("val");
assertTrue(filter.accept(key, v));  // Only checks happy path

// Missing test for deleted keys — the bug goes undetected
```