---
name: profile-activation-and-condition-logic
description: When profile activation contains multiple AND conditions (file exists
  AND property match), test that ALL conditions must be satisfied — not just the first
  one. The TG should verify that combined activations correctly require every condition
  to be met.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# profile-activation-and-condition-logic

## Instructions

# Profile Activation AND-Condition Logic

## Instructions

- WHEN the TG encounters a profile activation configuration that combines multiple condition types (e.g., `<file>` + `<property>` + `<os>`) within a single `<activation>` block (implying AND logic), THEN the TG MUST write a test that verifies ALL conditions are evaluated, not just the first one.
- WHEN the code under test evaluates profile activations containing both a file existence condition (`<file><exists>...</exists></file>`) and a property condition (`<property><name>...</name><value>...</value></property>`), THEN the TG SHOULD write tests that:
  1. Verify the profile activates when ALL conditions are satisfied (file exists AND property matches).
  2. Verify the profile does NOT activate when ONLY the first condition is satisfied but a subsequent condition fails.
  3. Verify the profile does NOT activate when only a subset of conditions are met.
- WHEN testing a `ProfileActivator` or `ProfileSelector` that performs the activation check, THEN the TG MUST test activation objects with multiple conditions using a POM model configured in XML, loading it via `ModelBuilder` or a similar test harness (e.g., using `new ModelBuildingRequest()` with a test POM file).
- The TG SHOULD use `assertEquals(false, ...)` or `assertFalse(...)` combined with the `ProfileActivationContext` to verify the profile is NOT considered active when one condition among several is unsatisfied.
- **Common Pitfall**: Testing with only one condition type (e.g., only file activation) or only the "all satisfied" case fails to catch cases where the activation short-circuits after the first condition. The TG MUST explicitly test the case where the first condition is met but a subsequent condition is not.
- **Common Pitfall**: Directly testing the `FileProfileActivator.isActive()` or similar unit-level activator in isolation may miss the integration issue where the `ProfileSelector` or `ModelBuilder` combines the results incorrectly. The TG SHOULD test at the level where multiple activators are combined (e.g., via `ModelBuilder.build()` with a model that has multi-condition profiles).
- **Example (Correct)** — Test that profile with both file and property conditions does NOT activate when only one condition matches:
  ```java
  @Test
  void testProfileDoesNotActivateWhenOnlyFirstConditionMet() throws Exception {
      File pom = Resources.getResource("poms/factory/complex.xml");
      Model model = readModel(pom);
  
      Profile profile = model.getProfiles().get(0); // profile "two-conditions" with file + property
      
      ProfileActivationContext context = newProfileActivationContext( ... );
      // Set up context so file condition IS satisfied but property condition is NOT
      
      assertFalse(new DefaultProfileSelector().isActive(profile, context, ...));
  }
  ```
- **Example (Incorrect)** — Only testing the "all conditions met" case (which passes even with a broken short-circuit) but not the "first condition met but second fails" case:
  ```java
  // BAD: This test only checks the happy path
  @Test
  void testProfileActivatesWithBothConditions() throws Exception {
      // Both file and property are satisfied
      assertTrue(isActive(profile, contextWithBothSatisfied));
      // Missing: test where only file is satisfied but property is not
  }
  ```