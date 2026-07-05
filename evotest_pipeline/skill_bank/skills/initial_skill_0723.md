---
name: ordering-index-query-property-traversal
description: When querying an ordered property index that uses property traversal,
  the query results may be incomplete if the index storage mixes absolute and relative
  path handling. The test should verify that all expected results are found, including
  those where the indexed property appears on child selectors.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- ARGUMENT_VALIDATION
test_pattern: PARAMETRIC_TEST
---

# ordering-index-query-property-traversal

## Instructions

# Ordered Property Index Query Result Completeness

## Instructions

- WHEN the TG encounters a query test that uses an ordered property index (e.g., `OrderedPropertyIndex`) with a property constraint like `[property] = 'value'` and the query uses a selector that traverses child nodes (e.g., `/jcr:root/content//element(*, nt:base)`):
  - THEN the TG should verify that ALL matching nodes are returned by the query result, not just a subset.
  - Specifically, when nodes have the indexed property set on both the root path and a child path, ensure that the query returns results from BOTH paths.
  - Use `assertQuery` calls that check the exact set of expected paths using `containsInAnyOrder` or equivalent matching, not just existence of some results.
  - For the fixed code, the query `SELECT * FROM [nt:base] AS s WHERE ISDESCENDANTNODE(s, '/content') AND [property] = 'value'` should return paths under `/content` where the property is set, including both `/content/a` and `/content/b` etc.
  - Common pitfall: Only checking the FIRST matching path in the result set, or using a query that restricts the path to a particular node rather than traversing children. The test must use `ISDESCENDANTNODE` or a similar descendant traversal to capture all indexed entries.
  - Common pitfall: Using `path` constraint directly instead of descendant traversal — this can work for the root node but miss child nodes where the same property value exists.
  - Example — Correct: An assertQuery that checks the query returns exactly `["/content/a", "/content/b", "/content/c"]` (paths where property='value').
  - Example — Incorrect: An assertQuery that only checks `["/content"]` or only one result, or a filter that excludes some results due to path ordering behavior in the index.