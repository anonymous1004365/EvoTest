---
name: template-proxy-param-type-validation
description: When a template/resource provider method uses generic type parameters
  to construct or query typed entities, the TG should test that all possible concrete
  type arguments (primitive wrappers, entity types, collections) are properly handled
  without casting or type metadata errors.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# template-proxy-param-type-validation

## Instructions

# Template Proxy Parameter Type Validation

## Instructions

- WHEN the TG encounters a class that acts as a **template or proxy** for database queries (e.g., methods named `count`, `existsById`, `findAll`, `save`, `delete`, etc.) and accepts a **generic type parameter `T`** (e.g., `<T> long count(Class<T> entityClass, ...)` or a template class parameterized as `SpannerTemplate<T>`):
  - THEN the TG should write a **parametric test** that verifies the template method works correctly for **each concrete type** in a set of representative types — including **primitive wrapper types** (`Integer.class`, `Long.class`, `String.class`, `Boolean.class`), **custom entity types**, and **collection types**.
  - The test should **construct the expected query/operation** (e.g., a `SELECT COUNT(*) FROM ...` statement or equivalent) for each type and verify the template method **validates, generates, or delegates correctly** for that type.
  - Verify that the method does **not throw an unexpected exception** (e.g., `IllegalArgumentException`, `NullPointerException`, `ClassCastException`) for any of the tested types.
  - On the fixed version, all tested types should succeed. On the buggy version, **at least one type** should fail (often a type that the template's metadata/proxy layer mishandles).

- **Common pitfalls to avoid**:
  - Testing only the "happy path" entity type (e.g., `Trade.class`) and ignoring **non-entity types** like `Integer.class` or `String.class`.
  - Assuming the template method only works with annotated entity classes — it may also be called with simple types for analytic queries, and the metadata layer must handle those.
  - Forgetting to test types that require **generic type resolution** (e.g., parameterized types where the template must unwrap the type argument from a proxy).
  - Writing a single test with one entity type and assuming all types behave the same way.

- **Correct example** (Java/JUnit 5):

```java
@ParameterizedTest
@ValueSource(classes = {Integer.class, String.class, Long.class, Boolean.class, Trade.class})
void countWithVariousTypesShouldNotThrow(Class<?> entityClass) {
    when(spannerTemplate.count(entityClass)).thenReturn(5L);
    long result = spannerTemplate.count(entityClass);
    assertEquals(5L, result);
}
```

- **Incorrect example** (only tests one entity type, missing the bug):

```java
@Test
void countShouldWork() {
    when(spannerTemplate.count(Trade.class)).thenReturn(5L);
    assertEquals(5L, spannerTemplate.count(Trade.class));
}
```

- **Bug symptom on buggy version**: The `count` method (or similar template method) internally tries to resolve the table name from the type's metadata. For simple types like `Integer.class`, the metadata may be `null` or throw `NullPointerException` or `IllegalArgumentException`. The fix typically adds a guard (null-check, fallback, or alternative resolution path) for types that do not have template metadata.