---
name: lazy-facade-type-description-delegation
description: When a TypePool.LazyFacade delegates type descriptions to another TypePool,
  tests must verify that methods like describe() and findPool() handle the delegation
  correctly, especially for anonymous/inner types and non-enclosed types. This skill
  teaches how to test proxy delegation patterns where a proxy delegates to an underlying
  lazy pool.
code_tags:
- TYPE_CONVERSION
- STATE_MUTATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# lazy-facade-type-description-delegation

## Instructions

# Lazy Facade Type Description Delegation

## Instructions

- WHEN the TG encounters a `TypePool.LazyFacade` or similar proxy/facade pattern that delegates `describe()` or related methods to an underlying `TypePool` (e.g., `LazyTypePool`):
  - THEN the TG should test that the facade correctly delegates type description calls for various type scenarios, especially:
    - `describe(typeName)` with anonymous class types (e.g., `"some.package.OuterClass$1"`)
    - `describe(typeName)` with non-enclosed types (e.g., `"java.lang.Object"`)
    - `findPool(typeName)` when the underlying pool fails or is absent
  - THEN the TG should verify that the returned `TypeDescription` is non-null and correctly represents the requested type
  - THEN the TG should verify that when the underlying pool's method returns null (e.g., `describe()` returns null for unknown types), the facade handles null gracefully without throwing a `NullPointerException`
  - THEN the TG should test the facade's behavior when the backing pool has not yet been resolved (is null), ensuring a graceful fallback or error

- Common pitfalls to avoid:
  - Testing only delegation with simple types (e.g., `"java.lang.String"`) without testing anonymous/inner types that have different naming conventions
  - Forgetting to test what happens when the underlying pool returns null (the facade should handle this cleanly)
  - Assuming the backing pool is always initialized and non-null when the facade delegates
  - Not testing edge cases like non-enclosed anonymous types that bypass standard type resolution paths

- Example of a correct test:
  ```java
  @Test
  public void testNonEnclosedAnonymousType() {
      TypePool.LazyFacade lazyFacade = new TypePool.LazyFacade(...);
      // Anonymous class types with numeric suffixes like "OuterClass$1"
      TypeDescription typeDescription = lazyFacade.describe("some.package.OuterClass$1");
      assertNotNull("Anonymous type description should not be null", typeDescription);
      // Also test that pool resolution works for these types
  }
  ```

- Example of an incorrect/insufficient test:
  ```java
  @Test
  public void testDescribeSimpleType() {
      TypePool.LazyFacade lazyFacade = new TypePool.LazyFacade(...);
      // Only testing a simple type, missing the anonymous/inner type edge cases
      TypeDescription typeDescription = lazyFacade.describe("java.lang.Object");
      assertNotNull(typeDescription);
  }
  ```