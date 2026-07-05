---
name: filter-always-false-on-null-property
description: WHEN the TG encounters a Filter.restrictProperty or FilterImpl.restrictProperty
  where a PropertyValue could be null or have a null value, THEN they should test
  that calling the method with such null values leads to isAlwaysFalse() being true.
  This prevents NullPointerException during query planning.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# filter-always-false-on-null-property

## Instructions

# Filter AlwaysFalse on Null Property

## Instructions

- WHEN the TG sees `Filter.restrictProperty(String, Operator, PropertyValue)` or `FilterImpl.restrictProperty(String, Operator, PropertyValue)` being called in a query planning/execution code path
- THEN the TG should write a test that calls `restrictProperty` with a `PropertyValue` that is null or whose internal value is null, and verify that the filter correctly sets itself to "always false" via `filter.isAlwaysFalse()`
- Specifically, if `PropertyValue` is of type `STRING` but its internal value is `null` (e.g., obtained from `PropertyValues.newString(null)`), the filter should still handle this gracefully and become `isAlwaysFalse()`, rather than throwing a `NullPointerException`
- The test should use `Operator.EQUAL` or `Operator.NOT_EQUAL` with the null-valued property value
- Common pitfalls: 
  - Testing only with non-null property values and assuming the filter handles null correctly
  - Not checking `isAlwaysFalse()` after restricting with null-valued properties
  - Assuming that a null `PropertyValue` object itself would be caught — the bug is specifically about a non-null `PropertyValue` that wraps a null value

### Correct Example (catches the bug):
```java
public void mvp() throws Exception {
    FilterImpl f = new FilterImpl(null, null, null, false);
    PropertyValue p = PropertyValues.newString(null);
    f.restrictProperty("test", Operator.EQUAL, p);
    assertTrue(f.isAlwaysFalse());
}
```

### Incorrect Example (misses the bug):
```java
public void mvp() throws Exception {
    FilterImpl f = new FilterImpl(null, null, null, false);
    PropertyValue p = PropertyValues.newString("someValue");
    f.restrictProperty("test", Operator.EQUAL, p);
    // Only tests non-null values; won't catch the NPE with null values
    assertFalse(f.isAlwaysFalse());
}
```