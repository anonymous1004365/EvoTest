---
name: pojo-generic-field-type-validation
description: When analyzing POJO types that contain generic fields (like Collection<String>),
  test that TypeExtractor.createTypeInfo() correctly identifies the class as a PojoTypeInfo
  rather than falling back to GenericTypeInfo. This skill catches regressions where
  generic field types cause incorrect POJO type detection.
code_tags:
- VALIDATION
- GENERIC_TYPE_RESOLUTION
- POJO_TYPE_ANALYSIS
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# pojo-generic-field-type-validation

## Instructions

# POJO Generic Field Type Validation

## Instructions

- WHEN the TG encounters a class that should be a valid POJO (has a public no-arg constructor and all private fields have getters/setters) **AND** one or more of its fields use generic/parameterized types (e.g., `Collection<String>`, `List<Integer>`, `Map<String, Long>`)
- THEN the TG should write a test that passes the class to `TypeExtractor.createTypeInfo()` and asserts that the result is an instance of `PojoTypeInfo<?>`, not `GenericTypeInfo<?>`. The bug occurs because the type extractor fails to correctly handle parameterized types during POJO validation, falling back to treating the class as a generic type.
- The TG should include at least one test class with a field typed as `Collection<String>` (with getters and setters) and a boolean primitive field, plus a test method annotated with `@Test` that calls `TypeExtractor.createTypeInfo(TestClass.class)` and asserts `Assert.assertTrue(typeForClass instanceof PojoTypeInfo<?>)`.
- Common pitfalls to avoid:
  - Testing only primitives or String fields without generic type parameters — the bug specifically triggers when a POJO field has a parameterized type like `Collection<String>`.
  - Forgetting that the POJO must have a no-arg constructor for it to be considered valid.
  - Assuming that any valid Java bean is automatically detected as a PojoTypeInfo — the bug shows that parameterized fields cause incorrect fallback to GenericTypeInfo even when all other POJO criteria are met.
  - Testing with `TypeExtractor.getForObject()` instead of `TypeExtractor.createTypeInfo()` — the bug manifests specifically in `createTypeInfo()`.

### Correct Example (catches the bug)
```java
public static class PojoWithGenericFields {
    private Collection<String> users;
    private boolean favorited;

    public boolean isFavorited() { return favorited; }
    public void setFavorited(boolean favorited) { this.favorited = favorited; }
    public Collection<String> getUsers() { return users; }
    public void setUsers(Collection<String> users) { this.users = users; }
}

@Test
public void testPojoWithGenericFields() {
    TypeInformation<?> typeForClass = TypeExtractor.createTypeInfo(PojoWithGenericFields.class);
    Assert.assertTrue("POJO with generic fields should be detected as PojoTypeInfo, not GenericTypeInfo",
        typeForClass instanceof PojoTypeInfo<?>);
}
```

### Incorrect Example (misses the bug)
```java
// Tests only basic types, not generic parameterized fields — won't catch the bug
public static class SimplePojo {
    private int count;
    public int getCount() { return count; }
    public void setCount(int c) { this.count = c; }
}

@Test
public void testSimplePojo() {
    TypeInformation<?> typeForClass = TypeExtractor.createTypeInfo(SimplePojo.class);
    Assert.assertTrue(typeForClass instanceof PojoTypeInfo<?>);
    // SimplePojo works fine — the bug only appears with generic fields
}
```