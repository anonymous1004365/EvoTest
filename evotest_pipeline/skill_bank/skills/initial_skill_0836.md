---
name: privilege-aggregate-ordering-validation
description: WHEN the TG encounters code that builds aggregate privilege definitions
  by combining sub-privilege names/bits (e.g., jcr:write combining jcr:modifyProperties,
  rep:addProperties, etc.), THEN the TG should test that the declared aggregate privileges
  are returned in the correct canonical order, not in the arbitrary registration order.
  This skill addresses the common pitfall where aggregate privilege definitions store
  sub-privileges in insertion order (which may be alphabetical or user-specified)
  but the contract expects a specific canonical ordering.
code_tags:
- PRIVILEGE_AGGREGATE_BUILDING
test_pattern: STATE_TEST
---

# privilege-aggregate-ordering-validation

## Instructions

# Privilege Aggregate Ordering Validation

## Instructions

- WHEN the TG encounters code that registers or builds aggregate privilege definitions (e.g., `PrivilegeBits`, `PrivilegeBitsProvider`, or any method that constructs an aggregate privilege from a set of declared aggregate names like `jcr:write` with aggregate names `[jcr:modifyProperties, rep:addProperties, rep:alterProperties, rep:removeProperties, jcr:addChildNodes, jcr:removeChildNodes, jcr:removeNode]`)
- THEN the TG should write a test that:
  1. Registers (or simulates registering) an aggregate privilege with its declared aggregate names
  2. Retrieves the aggregated privilege names back via the method that returns the declared aggregates (e.g., `getAggregatedPrivileges()`, `getDeclaredAggregate()`, or equivalent)
  3. Verifies the returned list/set of aggregate privilege names matches the **canonical/expected ordering** — not just set equality, but that the iteration order matches
  4. For the specific case of `jcr:write`, the expected canonical order is: `[jcr:modifyProperties, rep:addProperties, rep:alterProperties, rep:removeProperties, jcr:addChildNodes, jcr:removeChildNodes, jcr:removeNode]`
- Common pitfalls to avoid:
  - Testing only that the aggregate contains all expected names (using set comparison or `containsAll`) without checking ordering
  - Assuming the order of registration is the order returned
  - Using `HashSet` or other unordered collections in the actual implementation when the API contract guarantees ordering
  - Not testing that aggregate privilege resolution during upgrades preserves the original canonical ordering
- Concrete example of correct test:
  ```java
  // Correct: checks both content AND order of aggregated privileges
  List<String> expected = Arrays.asList(
      "jcr:modifyProperties", "rep:addProperties", "rep:alterProperties",
      "rep:removeProperties", "jcr:addChildNodes", "jcr:removeChildNodes",
      "jcr:removeNode"
  );
  List<String> actual = privilegeBitsProvider.getAggregatedPrivileges("jcr:write");
  assertEquals("Aggregate privilege names must be in canonical order", expected, actual);
  ```
- Concrete example of incorrect (insufficient) test:
  ```java
  // Incorrect: only checks set membership, misses ordering bugs
  Set<String> expected = new HashSet<>(Arrays.asList(
      "jcr:modifyProperties", "jcr:addChildNodes", "jcr:removeChildNodes",
      "jcr:removeNode", "rep:addProperties", "rep:alterProperties",
      "rep:removeProperties"
  ));
  Set<String> actual = new HashSet<>(privilegeBitsProvider.getAggregatedPrivileges("jcr:write"));
  assertEquals(expected, actual); // passes even if order is wrong!
  ```
- The triggering test expects ordered comparison (using `toString()` or `List.equals()`), so the test should verify the exact `List` or `Collection` ordering, not rely on unordered set comparison.