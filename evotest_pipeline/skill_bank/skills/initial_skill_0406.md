---
name: index-definition-property-type-exclusion
description: Guides the TG to test exclusion query filters when index definitions
  use property type arrays for inclusion/exclusion. When Oak Lucene index definitions
  have includePropertyTypes/excludePropertyNames configured, the TG should verify
  that nodes with excluded types are correctly filtered from query results.
code_tags:
- STATE_MUTATION
- VALIDATION
- BOUNDARY_CHECK
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# index-definition-property-type-exclusion

## Instructions

# Index Definition Property Type Exclusion

## Instructions

- WHEN the TG encounters Oak Lucene index code that handles `includePropertyTypes` or `excludePropertyNames` in index definitions (e.g., `LuceneIndexEditorContext`, `LuceneIndexEditor`, `LuceneIndexProvider`, `IndexDefinition`)
- THEN the TG should write a test that:
  1. Creates a Lucene index definition with specific `includePropertyTypes` configured (e.g., `PropertyType.STRING`)
  2. Inserts nodes with properties of both the included type (e.g., `PropertyType.STRING` via `jcr:title`) and an excluded type (e.g., `PropertyType.UNDEFINED` or `PropertyType.BINARY`)
  3. Executes a query that filters by `excludeNodes` with the excluded node's path
  4. Asserts that the query results contain only the included-type node and NOT the excluded-type node
  5. On the buggy version, this test should fail (result set size mismatch: expected `<expectedCount>` but was `<actualCount>`)

- WHEN testing `excludeNodes` or `isNodeType` exclusion queries with property type restrictions
- THEN the TG must verify that:
  - The exclusion filter correctly removes nodes whose properties match the excluded type
  - The exclusion filter correctly keeps nodes whose properties match the included type
  - The `includePropertyTypes` setting in the `IndexDefinition` is properly respected during query execution

- Common pitfalls to avoid:
  - Testing exclusion queries without setting up both included-type and excluded-type nodes — the bug only manifests when nodes have a mix of property types
  - Assuming that `includePropertyTypes` only affects indexing but not query-time filtering — the fix may also need changes in query evaluation
  - Using only `String` property types in test data — include at least one node with a non-included property type (e.g., `UNDEFINED`) to trigger the bug
  - Not configuring the Lucene index definition properly: the `includePropertyTypes` must be set in the index definition node before indexing/querying
  - Forgetting that the oak-run indexing may skip nodes whose properties don't match `includePropertyTypes`, leading to missing entries in the index

- Example test pattern:

  ```java
  // Set up index with includePropertyTypes = [PropertyType.STRING]
  NodeBuilder index = ...
  ValueFactory vf = ...
  index.setProperty(LuceneIndexConstants.INCLUDE_PROPERTY_TYPES, 
      new Value[]{vf.createValue(PropertyType.STRING)});

  // Create node with a STRING property (should be indexed)
  NodeBuilder included = ...
  included.setProperty("jcr:title", "included");

  // Create another type node (e.g., UNDEFINED) that should NOT be indexed
  NodeBuilder excluded = ...
  excluded.setProperty("foo", "bar", PropertyType.UNDEFINED);
  // Tag this node for exclusion
  excluded.setProperty("exclude", true);

  // Query and verify
  // On buggy version: result set may include excluded node → test fails
  // On fixed version: result set correctly excludes the excluded node → test passes
  ```