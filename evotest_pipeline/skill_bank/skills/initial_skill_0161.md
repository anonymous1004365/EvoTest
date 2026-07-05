---
name: row-level-security-decorator-parameter-type-validation
description: When a repository decorator validates parameters using a type-restricted
  method that requires separate handling for different types (e.g., CtTypeReference
  vs String parameter types), the test should verify that all valid parameter types
  are accepted and invalid types reject correctly.
code_tags:
- VALIDATION
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# row-level-security-decorator-parameter-type-validation

## Instructions

# Row-Level Security Decorator Parameter Type Validation

## Instructions

- WHEN the TG encounters a repository decorator or similar wrapper that intercepts method calls (e.g., `findAll`, `findOne`, `delete`) and performs row-level security checks based on parameter types
- THEN the TG should:
  1. Identify ALL valid parameter types for the intercepted method (e.g., `String`, `CtTypeReference`, `List<String>`)
  2. Test each parameter type separately to ensure the decorator correctly processes each type
  3. Verify that unsupported or unexpected types are handled gracefully (e.g., passed through without modification or rejected with an appropriate exception)
  4. For methods that apply security filtering differently based on the parameter's actual type (e.g., `findAll(Iterable<String> ids)` vs `findAll(CtTypeReference type)`), write separate test cases for each signature variant
  5. Verify that the security decorator does NOT unintentionally modify, filter, or throw exceptions for unexpected parameter types — only the specifically supported types should trigger security filtering logic

- Common pitfalls to avoid:
  - Testing only the most common parameter type (e.g., only `String` types when the method also accepts `CtTypeReference`)
  - Assuming that a single test case covers all parameter variants
  - Overlooking that the decorator might need to distinguish parameter types at runtime via `instanceof` checks, and each branch must be tested

- Correct example:
  ```java
  @Test
  void testFindAllWithStringIds() {
      DecoratedRepository repo = new DecoratedRepository(delegate);
      Iterable<String> ids = List.of("id1", "id2");
      when(delegate.findAll(ids)).thenReturn(...);
      
      // Verify security filtering is applied for String IDs
      assertThat(repo.findAll(ids)).containsExactly(...);
  }
  
  @Test
  void testFindAllWithTypeReference() {
      DecoratedRepository repo = new DecoratedRepository(delegate);
      CtTypeReference typeRef = mock(CtTypeReference.class);
      
      // Verify that type reference queries are passed through or handled differently
      repo.findAll(typeRef);
      verify(delegate).findAll(typeRef);
  }
  ```

- Incorrect example:
  ```java
  // BAD: Only tests with the generic Iterable
  @Test
  void testFindAll() {
      // Tests with Iterable<String> but fails to test CtTypeReference
      // Missing coverage for the instanceof check that branches behavior
  }
  ```