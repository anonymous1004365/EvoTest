---
name: property-builder-assignfrom-preserves-identity
description: ''
code_tags:
- TYPE_CONVERSION
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# property-builder-assignfrom-preserves-identity

## Instructions

# PropertyBuilder.assignFrom() Must Preserve Identity for Generic Types

## Instructions

- WHEN the TG encounters code that uses `PropertyBuilder.assignFrom(PropertyState)` to copy a property of a generic type (i.e., `Type.DATE`, `Type.NAME`, `Type.PATH`, `Type.URI`, `Type.REFERENCE`, `Type.WEAKREFERENCE`) — types where `type.tag()` falls into the `default:` branch in `getPropertyState()`:
  - THEN the TG should test that `assignFrom(source)` followed by `getPropertyState()` produces a `PropertyState` that is `.equals()` to the `source` (identity preservation).
  - Specifically, the TG should verify that when assigning FROM a `GenericPropertyState` (or `MultiGenericPropertyState`) OF THE SAME generic type as the builder's target type, no `ClassCastException` occurs.
  - Use `PropertyBuilder.scalar(Type.DATE)` / `PropertyBuilder.array(Type.DATE)` with a `source` created by `GenericPropertyState.dateProperty(name, value)` or `MultiGenericPropertyState.dateProperty(name, list)`.

- WHEN building a test for `assignFrom`:
  - THEN include **at minimum** the `Type.DATE` case for both scalar and array, because the buggy code failed specifically when a `GenericPropertyState` with type `DATE` was assigned into a `PropertyBuilder` also targeting `Type.DATE`.
  - Include the assertion: `assertEquals(source, builder.getPropertyState());` — this verifies that the built property matches the source exactly.

- WHEN considering which values to test with:
  - THEN test with a Date string value (e.g., `"1970-01-01T00:00:00.000Z"`) to match the known failing case.
  - Test both scalar and array variants: `PropertyBuilder.scalar(Type.DATE)` and `PropertyBuilder.array(Type.DATE)`.

- Common pitfalls to avoid:
  - Testing ONLY with primitive-like types (`Type.STRING`, `Type.LONG`, `Type.DOUBLE`, `Type.BOOLEAN`, `Type.BINARY`, `Type.DECIMAL`) — these are safe because they have dedicated cases in the `getPropertyState()` switch statement. The bug only manifests for generic types that fall into the `default:` branch.
  - Assuming that assigning a generic-type property to a builder of the same generic type is a no-op conversion. The buggy code called `setValues()` on the raw values without converting them appropriately, causing a `ClassCastException` when the values were cast to `String` via the `default:` branch.
  - Forgetting to set the array flag correctly: `builder.assignFrom(source)` must correctly detect `source.isArray()` and set `isArray = true` on the builder.

### Correct example (scalar DATE identity test):
```java
@Test
public void testAssignFromDate() {
    String date = "1970-01-01T00:00:00.000Z";
    PropertyState source = GenericPropertyState.dateProperty("foo", date);
    PropertyBuilder builder = PropertyBuilder.scalar(Type.DATE);
    builder.assignFrom(source);
    assertEquals(source, builder.getPropertyState());
}
```

### Correct example (array DATE identity test):
```java
@Test
public void testAssignFromDates() {
    String date1 = "1970-01-01T00:00:00.000Z";
    String date2 = "1971-01-01T00:00:00.000Z";
    PropertyState source = MultiGenericPropertyState.dateProperty("foo", Arrays.asList(date1, date2));
    PropertyBuilder builder = PropertyBuilder.scalar(Type.DATE);
    builder.assignFrom(source);
    assertEquals(source, builder.getPropertyState());
}
```

### Incorrect approach (insufficient — only tests non-generic types):
```java
// This test passes even on the buggy version and doesn't catch the bug!
@Test
public void testAssignFromLong() {
    PropertyState source = LongPropertyState.createLongProperty("foo", 42L);
    PropertyBuilder builder = PropertyBuilder.scalar(Type.STRING);
    builder.assignFrom(source);
    assertEquals(StringPropertyState.stringProperty("foo", "42"), builder.getPropertyState());
}
```