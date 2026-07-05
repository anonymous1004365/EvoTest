---
name: multi-property-or-query-type-filtering
description: For PropertyIndexLookup.getLocalPaths() when a filter has multiple OR
  conditions on the same property, the query incorrectly filters by the first condition's
  type instead of combining types. Tests should verify all OR values produce correct
  results regardless of their type.
code_tags:
- NULL_CHECK
- VALIDATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# multi-property-or-query-type-filtering

## Instructions

# Multi-Property OR Query Type Filtering

## Instructions

- WHEN the TG encounters query index code that processes `Filter.PropertyRestriction` objects from `filter.getPropertyRestrictions()` and builds paths for a property index lookup
- AND the filter contains multiple OR conditions on the same property (e.g., `property IN (value1, value2, ...)`) where different values may have different types (e.g., String vs Long vs other types)
- THEN the TG should write a test that:
  1. Creates a node with the property set to each of the different OR values
  2. Executes the OR query with mixed-type values and verifies ALL matching nodes are returned
  3. Specifically, if the property values have different types (e.g., "foo" is a String and "bar" is also a String, OR "42" is a String and 42 is a Long), the test must verify the query finds nodes for ALL values, not just those matching the first value's type
  4. Expect the correct behavior (after fix) to return all matching nodes; the buggy behavior returns only nodes matching the first value's type

- Common pitfalls:
  - Testing only with values of the same type (e.g., all Strings) — this misses the bug entirely
  - Forgetting to check the type returned by `property.getType()` for each restriction — the bug is in `getType()` returning only the FIRST restriction's type instead of considering all of them
  - Using `jcr:contains` or `LIKE` conditions instead of proper `=` or `IN` conditions — the bug triggers specifically with `PropertyRestriction` objects where `getType()` is called
  - Assuming the query result size alone is sufficient — verify the actual paths/nodes returned contain all expected values

- **Correct test pattern** (for fixed version):
```java
// Setup: create nodes with property values of different types
// e.g., node1 has xyz="foo" (String), node2 has xyz="bar" (String)
// Query: SELECT * FROM [nt:base] WHERE [xyz] IN ("foo", "bar")
// Verify: both node1 and node2 are in results

// If values have different types:
// e.g., node1 has xyz="42" (String), node2 has xyz=42 (Long)
// Query: SELECT * FROM [nt:base] WHERE [xyz] IN ("42", 42)
// Verify: both node1 and node2 are in results
```

- **Incorrect test pattern** (would miss the bug):
```java
// ❌ Only tests with same-type values — doesn't exercise the bug
// Query: SELECT * FROM [nt:base] WHERE [xyz] IN ("foo", "bar")
// WHERE all values are Strings — the bug only manifests when type differs
// OR only tests with a single value — bug requires multiple OR conditions
```