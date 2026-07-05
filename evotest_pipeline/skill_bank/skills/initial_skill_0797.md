---
name: traversing-index-relative-property-query
description: When writing tests for traversing index queries with multiple relative
  properties on the same selector, test that the result includes nodes matching all
  relative property constraints simultaneously. The existing test structure uses testQuery
  method from AbstractQueryTest to build SQL2 queries and verify result sets against
  node definitions.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# traversing-index-relative-property-query

## Instructions

# Traversing Index Query with Multiple Relative Properties

## Instructions

- WHEN the TG encounters a traversing index query test that uses multiple relative properties on the same selector (e.g., `SELECT * FROM [nt:base] WHERE property1 = 'a' AND property2 = 'b'` where property1 and property2 are relative paths like `myProp/childNode`), and the test sets up a node hierarchy with those properties under different intermediate parent nodes:

  - THEN the TG should verify that the query result includes the node that matches ALL relative property constraints simultaneously. For example, if two relative properties use the same intermediate path segment (e.g., `myProp/x` and `myProp/y`), the test should create a single child node that contains BOTH properties, and assert that this node appears in the query result.

  - The TG should NOT assume that properties defined under separate parent child nodes (e.g., node `child1` with property `x`, and separate node `child2` with property `y`) will match a query that requires both properties on the same node. The query's semantics require a single node to satisfy all property constraints.

  - The TG should use the test class's test infrastructure (like the `testQuery` method from `AbstractQueryTest`, which takes a SQL2 query string and a set of expected node paths) to build the test and verify the result set. When setting up test data, use `builder.child("nodeName").setProperty("relPath", "value")` to establish the necessary parent-child hierarchy.

- Common pitfalls to avoid:
  - Testing relative property constraints using properties defined across separate, independent sibling nodes rather than on the same descendant node. For `myProp/a` and `myProp/b`, both properties must exist under a single `myProp` child node.
  - Forgetting that the relative path segments (e.g., `myProp/x` and `myProp/y`) share the same intermediate parent (`myProp`), so the test node structure must reflect that shared ancestry.
  - Mistaking a `SELECT WHERE property = 'value'` test (which matches at any level) for a relative property test (which requires a specific parent-child relationship in the node hierarchy).
  
- Correct example:
  ```java
  // Setup: create a node with a child that has both properties on the SAME node
  builder.child("myNode").child("myProp")
      .setProperty("x", "a")
      .setProperty("y", "b");
  
  // Query with relative properties sharing the same intermediate parent
  String sql2 = "SELECT * FROM [nt:base] AS s " +
                "WHERE s.myProp/x = 'a' AND s.myProp/y = 'b'";
  
  // Expected result includes myNode (which has myProp child with both x and y)
  testQuery(sql2, ImmutableSet.of("/myNode"));
  ```

- Incorrect example (buggy pattern):
  ```java
  // BUG: properties set on separate children, not on the same descendant node
  builder.child("myNode").child("myProp").child("c1").setProperty("x", "a");
  builder.child("myNode").child("myProp").child("c2").setProperty("y", "b");
  
  // This would return 0 results because no single node has BOTH x and y
  String sql2 = "SELECT * FROM [nt:base] AS s " +
                "WHERE s.myProp/x = 'a' AND s.myProp/y = 'b'";
  ```