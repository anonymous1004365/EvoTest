---
name: thrift-key-constructor-null-validation
description: When constructing a domain Key from a Thrift TKey object, validate that
  the TKey's row, colFamily, and colQualifier fields are non-null before use. This
  skill helps catch missing null checks on Thrift deserialization inputs that would
  otherwise cause NullPointerException instead of clear IllegalArgumentException.
code_tags:
- VALIDATION
- NULL_CHECK
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# thrift-key-constructor-null-validation

## Instructions

# Thrift Key Constructor Null Validation

## Instructions

- WHEN the TG encounters a constructor that accepts a Thrift object (e.g., `TKey`) and copies its fields into a domain object (e.g., `Key`):
  - THEN the TG should verify that the constructor validates null text fields (e.g., `row`, `colFamily`, `colQualifier`) from the Thrift object before passing them to downstream methods (e.g., `Key`'s parent `Text` constructor).
  - Use `@Test(expected = IllegalArgumentException.class)` and call the constructor with a `TKey` whose `row` / `colFamily` / `colQualifier` is `null`.
  - The test should expect `IllegalArgumentException` (not `NullPointerException`) from the constructors that handle Thrift objects.
  - Include a test that confirms all three text fields (`row`, `colFamily`, `colQualifier`) each separately produce `IllegalArgumentException` when `null`.

- Common pitfalls:
  - Testing only one null field instead of all nullable string fields.
  - Writing a test that expects `NullPointerException` — the fix adds explicit null checks that throw `IllegalArgumentException`.
  - Testing with an empty string (`""`) instead of `null` — only `null` triggers the validation guard.
  - Testing the `Key(TKey)` constructor but forgetting to test the copy constructor's new `TKey`-based path if applicable.

- Correct example:
```java
@Test(expected = IllegalArgumentException.class)
public void testThrift_Invalid() {
  // Construct a TKey with null row — should trigger validation
  Key key = new Key(new TKey(null, new Text("cf"), new Text("cq"), new Text("cv"), 42l, false, false));
}
```

- Incorrect example (uses `NullPointerException` instead of `IllegalArgumentException`):
```java
@Test(expected = NullPointerException.class)
public void testThrift_NullRow() {
  Key key = new Key(new TKey(null, new Text("cf"), new Text("cq"), new Text("cv"), 42l, false, false));
}
```

- Also incorrect (testing empty string instead of null):
```java
@Test(expected = IllegalArgumentException.class)
public void testThrift_EmptyRow() {
  // Empty string "" is NOT null — validation only checks for null, not empty
  Key key = new Key(new TKey(new Text(""), new Text("cf"), new Text("cq"), new Text("cv"), 42l, false, false));
}
```