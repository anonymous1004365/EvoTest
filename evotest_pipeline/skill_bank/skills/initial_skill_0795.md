---
name: null-insert-charsequence-handling
description: When a class like AppendingStringBuffer has insert(int, Object) that
  dispatches to insert(int, String), insert(int, StringBuilder), or insert(int, StringBuffer),
  the TG should test null values for each CharSequence subtype to ensure the "null"
  literal string is inserted correctly rather than a NullPointerException being thrown.
code_tags:
- NULL_CHECK
- VALIDATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# null-insert-charsequence-handling

## Instructions

# Null Insert Handling for CharSequence Types

## Instructions

- WHEN the TG encounters an `insert(int offset, Object obj)` method that dispatches to specific `insert` overloads for `String`, `StringBuilder`, and `StringBuffer`
- THEN the TG MUST test inserting `null` for each of those CharSequence subtypes specifically (cast to the subtype), verifying that:
  - No `NullPointerException` is thrown
  - The string `"null"` is inserted at the specified offset position
  - The overall buffer length increases correctly (by 4 for "null")
- Common pitfalls:
  - ❌ Only testing `insert(offset, (String)null)` — this misses bugs in the `StringBuilder` and `StringBuffer` overloads which may throw NPE or handle null differently
  - ❌ Only testing `insert(offset, (Object)null)` — this dispatches through the Object overload, not the specific CharSequence overloads
  - ❌ Assuming all insert overloads delegate consistently when handling null — always test each specific null-typed call
- Correct approach:
```java
// Test null for each CharSequence subtype
AppendingStringBuffer asb = new AppendingStringBuffer("123456789");
asb.insert(5, (StringBuilder)null);
assertEquals("12345null6789", asb.toString());

asb = new AppendingStringBuffer("123456789");
asb.insert(5, (StringBuffer)null);
assertEquals("12345null6789", asb.toString());

asb = new AppendingStringBuffer("123456789");
asb.insert(5, (String)null);
assertEquals("12345null6789", asb.toString());

asb = new AppendingStringBuffer("123456789");
asb.insert(5, (Integer)null);  // tests Object overload
assertEquals("12345null6789", asb.toString());
```