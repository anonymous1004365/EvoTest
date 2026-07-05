---
name: subselect-mapping-type-conformance
description: When validating subselect/entity-mapping configurations, test that dynamically
  registered entity types comply with the required contract (e.g., implementing an
  interface or having a specific superclass), and that the code properly handles or
  rejects non-conforming types instead of failing with internal errors like ClassCastException
  or NullPointerException.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- EXCEPTION_HANDLING
- NULL_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# subselect-mapping-type-conformance

## Instructions

# Subselect Entity Mapping Type Conformance

## Instructions

- WHEN a subselect entity definition allows registering/adding arbitrary entity types (e.g., via a builder or configuration method that accepts Class<?> or CtType references)
- THEN the TG should test that non-conforming entity types (i.e., types that do NOT extend a required base class or implement a required interface) are correctly rejected, and that the registration of a conforming type proceeds without internal errors such as ClassCastException or NullPointerException during later processing (entity resolution, model building, query execution).

- **What to test**:
  1. Register an entity type that DOES extend the expected base class / implement the required interface → verify it is accepted and query execution succeeds.
  2. Register an entity type that does NOT extend the expected base class / implement the required interface → verify a meaningful exception (e.g., IllegalArgumentException, SubqueryException) is thrown at registration time or before query execution, and NOT an internal error like ClassCastException or NullPointerException.
  3. Test with both plain Class<?> references and dynamically built types (e.g., from CtTypeReference or similar type metadata) to ensure both paths are covered.

- **Common pitfalls**:
  - Testing only the happy path (conforming types) and missing the negative case where non-conforming types cause internal crashes.
  - Assuming the API validates at registration time when in fact validation only happens lazily (e.g., during query execution or entity resolution) → test both registration and execution phases.
  - Not testing with the same object/entity configuration being used in an actual subselect query (e.g., via `FROM` clause with the subselect entity) to trigger lazy validation paths.

- **Example** (Java/JUnit 5):
  ```java
  // Correct: tests rejection of non-conforming type at registration
  @Test
  void testRejectsNonConformingEntityType() {
      EntityViewSetting<?, ?> setting = ...;
      // Suppose only types extending BaseEntity are allowed
      assertThrows(IllegalArgumentException.class, () -> {
          setting.addSubselectEntity(NonConformingEntity.class);
      });
  }
  
  // Correct: tests that conforming type works end-to-end
  @Test
  void testConformingEntitySubselect() {
      EntityViewSetting<?, ?> setting = ...;
      setting.addSubselectEntity(ConformingEntity.class);
      // Build the query and execute
      CriteriaBuilder<?> cb = cbf.create(em, ConformingEntity.class);
      // Verify the query runs without ClassCastException
      assertDoesNotThrow(() -> cb.getQuery());
  }
  
  // Incorrect: only tests the happy path, missing the rejection scenario
  @Test
  void testOnlyHappyPath() {
      EntityViewSetting<?, ?> setting = ...;
      setting.addSubselectEntity(ConformingEntity.class);
      // Missing: what happens with NonConformingEntity.class?
  }
  
  // Incorrect: assumes validation happens at addSubselectEntity() time
  // when in fact it happens later during query execution
  @Test
  void testAssumesEarlyValidation() {
      EntityViewSetting<?, ?> setting = ...;
      // This might NOT throw because validation is lazy
      setting.addSubselectEntity(NonConformingEntity.class);
      // The actual failure (e.g., ClassCastException) occurs later
  }
  ```

- **What errors to expect on the buggy version**: registration of a non-conforming entity type leads to a `ClassCastException`, `NullPointerException`, or `IllegalArgumentException` with an unhelpful message during subsequent query construction or execution, rather than a clear rejection at the API boundary.