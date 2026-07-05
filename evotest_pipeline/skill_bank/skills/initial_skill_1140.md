---
name: creator-collector-property-type-validation
description: When a CreatorCollector merges property-based and delegating/string-based
  creators, it must validate that the property types are compatible with the existing
  creator. Test that adding a creator with incompatible property types (e.g., a creator
  that takes a non-delegating/non-property type) is correctly rejected or handled,
  preventing silent overwrites or state corruption.
code_tags:
- VALIDATION
- STATE_MUTATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# creator-collector-property-type-validation

## Instructions

# CreatorCollector Property Type Validation

## Instructions

WHEN the Test Generator encounters a `CreatorCollector` or similar creator-collection logic that accumulates multiple creator methods (e.g., `addPropertyCreator`, `addDelegatingCreator`, `addStringCreator`) and performs deduplication or compatibility checks via methods like `verifyNonDup`:

- THEN the TG should test that when two creators are registered with the **same** name/index but **incompatible types** (one property-based with specific value types, another delegating or string-based), the second registration correctly fails or is handled without corrupting the previously registered creator's state.

- Specifically, test the scenario where:
  1. A creator is first registered with explicit property types (e.g., `int.class`, `String.class`).
  2. A second creator with the **same name** but **conflicting types** (e.g., a delegating creator with different type parameters, or a property creator with different property count) is attempted.
  3. The test should verify that:
     - The second registration is **rejected** (throws an `IllegalArgumentException` or similar).
     - The **first creator's state remains intact** — the previously registered creator details (property names, types, order) are not overwritten or corrupted.

- Include concrete examples: test with a `CreatorCollector` instance, add a creator with two properties of types `Integer.class` and `String.class`, then attempt to add a conflicting creator with the same name but different property structure.

- Common pitfalls to avoid:
  - ❌ Testing only one creator registration (no conflict scenario).
  - ❌ Only verifying that an exception is thrown, without also verifying that the original creator's properties are preserved.
  - ❌ Using mocked `CreatorCollector` objects instead of real instances that exercise `verifyNonDup` logic.
  - ❌ Testing only with identical types (no actual type mismatch).

- Correct approach:
  ```java
  // Example: Verify rejection of conflicting creator and preservation of first creator's state
  CreatorCollector collector = new CreatorCollector(...);
  // Register first creator with specific property types
  collector.addPropertyCreator("prop1", ...); // e.g., with int, String params
  // Attempt to register conflicting creator with same name but different/delegating types
  assertThrows(IllegalArgumentException.class, () -> {
      collector.addDelegatingCreator("prop1", ...); // conflicting type
  });
  // Verify first creator's properties are still intact
  assertEquals(Integer.class, firstCreator.propertyType(0));
  assertEquals(String.class, firstCreator.propertyType(1));
  ```

- Incorrect approach:
  ```java
  // ❌ Only testing one creator
  CreatorCollector collector = new CreatorCollector(...);
  collector.addPropertyCreator("prop1", ...);
  // No conflict test
  
  // ❌ Only checking exception, not state preservation
  CreatorCollector collector = new CreatorCollector(...);
  collector.addPropertyCreator("prop1", ...);
  assertThrows(IllegalArgumentException.class, () -> {
      collector.addDelegatingCreator("prop1", ...);
  });
  // ❌ Missing: verify first creator's state preserved
  ```