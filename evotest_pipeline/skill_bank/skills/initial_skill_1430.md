---
name: following-key-visibility-validation
description: When testing Key.followingKey() with PartialKey.ROW_COLFAM_COLQUAL_COLVIS,
  verify that the resulting visibility field is a valid ColumnVisibility expression
  that does not contain invalid null byte (0x00) characters. Otherwise, any downstream
  use of the followingKey result (e.g., toString(), ColumnVisibility parsing) will
  throw a BadArgumentException.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# following-key-visibility-validation

## Instructions

# Following Key Visibility Validation

## Instructions

- WHEN the TG encounters a call to `Key.followingKey(PartialKey.ROW_COLFAM_COLQUAL_COLVIS)` on a `Key` object that has a non-empty `colVisibility`
- THEN the TG should verify that the resulting key's `colVisibility` byte array does not contain a null byte (0x00) appended by `followingArray()`. The method `followingArray(byte[])` appends a `0x00` byte, which when interpreted as a column visibility expression, will be rejected by `ColumnVisibilityParser` in `ColumnVisibility.validate()` because `(byte)0x00` fails the `Authorizations.isValidAuthChar(c)` check, throwing a `BadArgumentException("bad character (0)", ..., ...)`.
- Specifically: `new Key("r", "f", "q", "v").followingKey(PartialKey.ROW_COLFAM_COLQUAL_COLVIS).toString()` should succeed without throwing `BadArgumentException`. The test should call `toString()` on the result of `followingKey` and assert that it returns the expected string format: `"r f:q [v%00;] " + Long.MAX_VALUE + " false"`.
- Common pitfalls: Assuming that `followingKey()` produces a valid key for all `PartialKey` values. For `ROW_COLFAM_COLQUAL_COLVIS`, the appended null byte makes the visibility field invalid as a `ColumnVisibility` expression. Also be aware that the `toString()` method internally calls `ColumnVisibility` parsing, which triggers the validation that catches the null byte.

### Correct Example
```java
public void testVisibilityFollowingKey() {
    Key k = new Key("r", "f", "q", "v");
    assertEquals(k.followingKey(PartialKey.ROW_COLFAM_COLQUAL_COLVIS).toString(),
        "r f:q [v%00;] " + Long.MAX_VALUE + " false");
}
```

### Incorrect Example (won't catch the bug)
```java
public void testFollowingKey() {
    Key k = new Key("r", "f", "q", "v");
    Key following = k.followingKey(PartialKey.ROW_COLFAM_COLQUAL_COLVIS);
    // Only checking that followingKey doesn't throw - won't catch bug:
    assertNotNull(following);
    // The bug is exposed only when toString() or ColumnVisibility parsing happens
}
```