---
name: following-key-visibility-buffer-overflow
description: When testing followingKey() on a Key with a non-empty column visibility,
  the method appends a null byte (0x00) to the visibility bytes without ensuring sufficient
  buffer space. Test with a Key that has a column visibility string to detect the
  ArrayIndexOutOfBoundsException or "bad character (0)" parse error.
code_tags:
- ARRAY_INDEX_ACCESS
- VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: INTERACTION_TEST
---

# following-key-visibility-buffer-overflow

## Instructions

# Following Key Visibility Buffer Overflow

## Instructions

- WHEN the TG encounters the `Key.followingKey(PartialKey part)` method that appends bytes to a copy of the column visibility (e.g., when `part` includes `COL_VIS` or `ROW_COLFAM_COLQUAL_COLVIS`)
- THEN the TG should test `followingKey()` with a Key that has a **non-null, non-empty column visibility** string, such as `new Key("r", "f", "q", "v")`, and verify that calling `followingKey(PartialKey.ROW_COLFAM_COLQUAL_COLVIS)` does not throw an exception and produces the expected output.
- The test should assert that the resulting key's string representation matches the expected format, e.g., `assertEquals("r f:q [v%00;] " + Long.MAX_VALUE + " false", k.followingKey(PartialKey.ROW_COLFAM_COLQUAL_COLVIS).toString());` — note the appended `%00` (null byte) and semicolon.
- **Common pitfalls to avoid:**
  - Do NOT test `followingKey()` only with Keys that have an empty column visibility (e.g., `new Key("r", "f", "q")`), or only with `PartialKey.ROW` or `PartialKey.ROW_COLFAM` — these paths do not exercise the visibility copy logic.
  - Do NOT assume that calling `followingKey()` will throw an exception on all inputs — the bug is triggered **only** when the column visibility is non-empty and the `part` parameter includes visibility (`COL_VIS` or any higher granularity that includes column visibility).
  - Do NOT forget to include the visibility in the Key constructor — use the 4-argument constructor `Key(String row, String cf, String cq, String cv)` or its byte/Text equivalents.

### Correct test example
```java
@Test
public void testVisibilityFollowingKey() {
  Key k = new Key("r", "f", "q", "v");
  assertEquals("r f:q [v%00;] " + Long.MAX_VALUE + " false",
      k.followingKey(PartialKey.ROW_COLFAM_COLQUAL_COLVIS).toString());
}
```

### Incorrect test example (won't catch the bug)
```java
// Only tests without visibility — no bug triggered
@Test
public void testFollowingKeyNoVisibility() {
  Key k = new Key("r", "f", "q");
  Key result = k.followingKey(PartialKey.ROW_COLFAM_COLQUAL_COLVIS);
  // This may pass even when the bug exists in the visibility branch
}
```