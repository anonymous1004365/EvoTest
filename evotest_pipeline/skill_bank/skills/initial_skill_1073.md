---
name: property-is-null-query-filter
description: When implementing query property condition filters (e.g., IS NULL / IS
  NOT NULL), test that the filter correctly includes nodes where the property is absent
  or null, and does not fail due to incorrect null handling. This skill helps catch
  cases where a property condition evaluation assumes a non-null value and returns
  false instead of correctly matching against absent/null properties.
code_tags:
- NULL_CHECK
- VALIDATION
- CONDITION_FILTER_MISMATCH
test_pattern: EXCEPTION_TEST
---

# property-is-null-query-filter

## Instructions

# Property IS NULL Query Filter Condition

## Instructions

- WHEN the TG encounters a query filter implementation that evaluates a property condition (e.g., checking if a property IS NULL or IS NOT NULL, or performing comparison operations like `<`, `>`, `<=`, `>=`, `=` on properties)
- THEN the TG should write a test that:
  1. Creates a node that does NOT have the property at all (property is absent/null)
  2. Creates another node that HAS the property with a concrete value
  3. Creates a query with a property condition on that property (e.g., `jcr:title IS NULL` or a comparison like `jcr:title > 'abc'`)
  4. Verifies that the query correctly returns only the expected nodes — i.e., the node with the absent property IS included in `IS NULL` results and excluded from `IS NOT NULL` results, and the node with the absent property IS excluded from comparison queries like `>`, `<`, etc.
  5. Specifically for IS NULL conditions: verify that when evaluating a property condition (implementing `PropertyCondition`), the `evaluate` method does NOT throw a `NullPointerException` (or return an incorrect `false`) when the property is absent/null from the node — instead, it must return `true` for `IS NULL` and `false` for `IS NOT NULL` and other comparisons.

- Common pitfalls to avoid:
  - **Only testing with properties that exist**: The TG might create test data where all nodes have the property, missing the case where the property is absent/null on some nodes.
  - **Assuming `evaluate()` handles null gracefully**: The TG might forget to test the `evaluate` method directly with a node that lacks the property, which can reveal NullPointerException or incorrect boolean return values.
  - **Testing only equality (`=` or `!=`)**: The filter bug often manifests with comparison operators like `<`, `>`, `<=`, `>=`, or `IS NULL`/`IS NOT NULL`, not just equality.
  - **Not testing with both absent and present properties**: When testing `IS NULL`, include nodes where the property is completely absent AND nodes where the property has a non-null value to verify correct filtering.

- Correct example:
```java
// Test both a node with the property and a node without it
Node nodeWithProperty = ...; // node that has "jcr:title" = "foo"
Node nodeWithoutProperty = ...; // node that does NOT have "jcr:title" at all  

// For IS NULL condition, the node without the property should be included
PropertyCondition isNull = new PropertyCondition("jcr:title", Operator.EQUAL, null);
assertTrue("Node without property should match IS NULL", isNull.evaluate(nodeWithoutProperty));
assertFalse("Node with property should NOT match IS NULL (unless value is also null)", isNull.evaluate(nodeWithProperty));
```

- Incorrect example:
```java
// BAD: Only testing with nodes that have the property
Node node1 = ...; // has "jcr:title" = "aaa"
Node node2 = ...; // has "jcr:title" = "bbb"

// This misses the case where a node doesn't have the property at all
// A buggy implementation might throw NPE or return false for absent properties
PropertyCondition isNull = new PropertyCondition("jcr:title", Operator.EQUAL, null);
// Should also test with a node that has no "jcr:title" property
```