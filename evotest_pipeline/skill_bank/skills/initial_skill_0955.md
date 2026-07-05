---
name: thrift-conversion-null-field-validation
description: Applies when converting Thrift objects to domain objects, the TG should
  validate that all required Thrift fields are non-null before passing them to domain
  constructors, expecting IllegalArgumentException on null fields.
code_tags:
- VALIDATION
- ARGUMENT_VALIDATION
- STATE_MUTATION
- THRIFT_CONVERSION_NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# thrift-conversion-null-field-validation

## Instructions

# Thrift Conversion Null Field Validation

## Instructions

- WHEN the TG encounters a method that converts a Thrift object (e.g., `org.apache.accumulo.proxy.thrift.Key`) to a domain object (e.g., `org.apache.accumulo.core.data.Key`) by extracting fields like `.row`, `.colFamily`, `.colQualifier`, `.colVisibility`, and `.timestamp` and passing them to a domain constructor
- THEN the TG MUST write an `EXCEPTION_TEST` that:
  1. Creates a new instance of the Thrift object with `new ThriftClass()`
  2. Sets `timestamp` to `Long.MAX_VALUE` (since timestamp is the only field that survives null check in the buggy version)
  3. Leaves all other required fields (`row`, `colFamily`, `colQualifier`, `colVisibility`) as `null` (the default for object fields in Thrift)
  4. Calls the conversion method/constructor (e.g., `new org.apache.accumulo.core.data.Key(thriftKey)`)
  5. Expects `IllegalArgumentException.class`
- The TG MUST also test individual null fields one at a time to ensure each required field is validated separately (e.g., set `row = null` while others are valid, then `colFamily = null`, etc.)
- Common pitfalls:
  - ❌ Testing only with all fields null — the bug might be that only some fields are checked. Test each field individually.
  - ❌ Testing with `timestamp = 0` or unset — the Thrift default for `timestamp` is 0, which might pass existing validation. Use `Long.MAX_VALUE` or another non-zero value to ensure timestamp doesn't interfere with other field checks.
  - ❌ Assuming the Thrift class has a specific constructor — Thrift auto-generated classes use a no-arg constructor, then set fields via setters or direct field access (`tk.row = ...`).
  - ❌ Confusing `org.apache.accumulo.proxy.thrift.Key` (proxy Thrift class) with `org.apache.accumulo.core.data.thrift.TKey` (core Thrift class) — verify which Thrift class the conversion method uses.

### Correct Example (detects bug)

```java
@Test(expected = IllegalArgumentException.class)
public void testThriftConversionRejectsNullRow() {
    org.apache.accumulo.proxy.thrift.Key tk = new org.apache.accumulo.proxy.thrift.Key();
    tk.row = null;
    tk.colFamily = "cf";
    tk.colQualifier = "cq";
    tk.colVisibility = "cv";
    tk.timestamp = Long.MAX_VALUE;
    new org.apache.accumulo.core.data.Key(tk);
}
```

### Incorrect Example (does NOT detect bug)

```java
// BAD: Only tests all-null, but timestamp default 0 might bypass some checks
@Test(expected = IllegalArgumentException.class)
public void testThriftConversionRejectsNullFields() {
    org.apache.accumulo.proxy.thrift.Key tk = new org.apache.accumulo.proxy.thrift.Key();
    // All fields default to null/0 — this might not trigger the right failure
    new org.apache.accumulo.core.data.Key(tk);
}
```

```java
// BAD: Only tests String constructor, not Thrift conversion
@Test(expected = IllegalArgumentException.class)
public void testKeyRejectsNullRow() {
    new org.apache.accumulo.core.data.Key(null, "cf", "cq", "cv", Long.MAX_VALUE);
}
```

### What the bug actually was
The buggy `Key(TKey tk)` constructor only validated that `tk.timestamp` was set (checking `!= 0`), but did NOT validate that `tk.row`, `tk.colFamily`, `tk.colQualifier`, and `tk.colVisibility` were non-null before passing them to the internal constructor. The fix adds null checks for all these fields, throwing `IllegalArgumentException` when any required field is null.