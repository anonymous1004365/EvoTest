---
name: entity-instantiator-ctor-arg-candidate-filtering
description: When a ClassGeneratingEntityInstantiator creates entity instances by
  matching constructor arguments, it must correctly filter candidate constructors
  to avoid selecting the wrong one when constructors have the same parameter count
  but different parameter types. Use this skill when testing instantiation logic with
  multiple constructors sharing the same arity.
code_tags:
- NULL_CHECK
- VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# entity-instantiator-ctor-arg-candidate-filtering

## Instructions

## Guidance

# Entity Instantiator Constructor Argument Candidate Filtering

## Instructions

- WHEN the TG encounters code that creates entity instances by reflecting constructors and matching constructor parameters to entity property names/types
  - THEN the TG should test with entity classes that have MULTIPLE constructors with the SAME number of parameters, where at least one parameter type differs (e.g., String vs CtTypeReference, or int vs long)
  - Concrete example: an entity with two constructors:
    - `Entity(String name, String value)` — one parameter String/int, another String/object
    - `Entity(CtTypeReference<?> name, CtTypeReference<?> value)` — both parameters are type references
  - The test must verify that the CORRECT constructor is selected based on actual parameter types, not just arity (parameter count)
  - WHEN the same entity property can match both a simple type and a complex type, test with both values to ensure the instantiator picks the right constructor without mis-matching parameter types

- WHEN the entity instantiator collects candidates by matching parameter count and then filters by type compatibility
  - THEN the TG should test the case where parameter type filtering fails to disambiguate, causing a fallback to the first remaining constructor which may be WRONG
  - Common pitfalls:
    - Testing only with entity classes that have a single constructor
    - Testing only with entity classes where all constructors have different parameter counts
    - Assuming that matching parameter count is sufficient to select the correct constructor
    - Not testing recursive entity definitions where properties are also entities with similar constructor patterns

- Concrete test pattern:
  - Create an entity class with two constructors of the same arity (e.g., both 2-arg):
    - Constructor A: `(String p1, Object p2)`
    - Constructor B: `(CtTypeReference<?> p1, CtTypeReference<?> p2)`
  - Create a nested/recursive scenario where the entity's property types match Constructor A but the instantiator selects Constructor B due to incomplete type filtering
  - Verify that instantiation succeeds and returns the entity with correct property values set (or verify that the correct constructor is invoked)
  - Expect the buggy version to throw an exception (e.g., `IllegalArgumentException`, `InstantiationException`, or `ClassCastException`) because the wrong constructor was chosen with incompatible parameter types

- Wrong test (does not catch the bug):
  ```java
  // Only tests with a single constructor — passes both buggy and fixed versions
  Entity entity = instantiator.createInstance(Entity.class);
  assertNotNull(entity);
  ```

- Correct test (catches the bug):
  ```java
  // Tests recursive entity with same-arity constructors having different types
  class RecursiveEntity {
      private final String name;
      private final RecursiveEntity child;
      
      public RecursiveEntity(String name, RecursiveEntity child) {
          this.name = name;
          this.child = child;
      }
      
      public RecursiveEntity(CtTypeReference<?> name, CtTypeReference<?> child) {
          this.name = name.toString();
          this.child = null;
      }
      // getters...
  }
  
  RecursiveEntity result = instantiator.createInstance(RecursiveEntity.class);
  assertEquals("expected", result.getName());
  assertNotNull(result.getChild());  // Fails with buggy version — wrong constructor used
  ```