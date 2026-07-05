---
name: equals-consistency-for-value-objects
description: When writing tests for classes that override equals() and have nullable
  reference fields, also test that equals() is consistent when comparing two objects
  with distinct non-null values for those fields. Without this, a NullPointerException
  or assertion error may occur when equals() is called on objects with different field
  values.
code_tags:
- NULL_CHECK
- EQUALS_OVERRIDE
test_pattern: STATE_TEST
---

# equals-consistency-for-value-objects

## Instructions

# Equals Consistency for Value Objects with Nullable Fields

## Instructions

- WHEN the class under test overrides `equals(Object)` and has at least one non-String reference-type field (e.g., `Locale`, `Date`, `URI`) that is used directly with `.equals()` on the casted parameter
- THEN the TG should write a test that:
  1. Creates two instances of the class that have the *same* value for the "primary" field (e.g., same `text`) but *different* values for the reference field (e.g., different `Locale` objects)
  2. Calls `assertEquals(false, instance1.equals(instance2))` and verifies it returns `false` without throwing any exception
  3. Also verifies the symmetric check: `assertEquals(false, instance2.equals(instance1))`
  4. Additionally, tests that objects with the same reference field value return `true`
- **Common pitfalls**:
  - Testing only with `null` reference fields, which may not exercise the `.equals()` call on the casted parameter's field
  - Testing only with the same values for all fields, which only verifies the "equal" case but not the "not equal" case
  - Forgetting to also test the "equal" case to confirm the method works correctly in both directions
  - Assuming that because a field is `final`, it can never be `null` or different between instances

## Example

Consider `StringValue` which has fields `String text` and `Locale locale`, and an `equals()` method:

```java
// Buggy equals() using locale.equals(stringValue.locale) — fails with NullPointerException when locale is null
public boolean equals(final Object obj) {
    if (obj instanceof StringValue) {
        StringValue stringValue = (StringValue) obj;
        return Objects.isEqual(text, stringValue.text) && locale.equals(stringValue.locale);
    }
    return false;
}
```

**Correct test** (catches the bug):

```java
@Test
public void equals()
{
    // Different locale values — catches NPE/bug if locale.equals() is called on null
    assertFalse(StringValue.valueOf("bla", Locale.FRANCE).equals(
        StringValue.valueOf("bla", Locale.CANADA)));
    
    // Same locale and same text — should be equal
    assertTrue(StringValue.valueOf("bla", Locale.FRANCE).equals(
        StringValue.valueOf("bla", Locale.FRANCE)));
    
    // Different text, same locale — should not be equal
    assertFalse(StringValue.valueOf("bla", Locale.FRANCE).equals(
        StringValue.valueOf("blo", Locale.FRANCE)));
}
```

**Incorrect test** (does NOT catch the bug):

```java
@Test
public void equals_bad()
{
    // Only tests with null locale — does not exercise locale.equals(otherLocale)
    assertFalse(StringValue.valueOf("foo").equals(StringValue.valueOf("bar")));
    
    // Only tests equality — does not test inequality with different locale values
    assertTrue(StringValue.valueOf("bla", Locale.FRANCE).equals(
        StringValue.valueOf("bla", Locale.FRANCE)));
}
```