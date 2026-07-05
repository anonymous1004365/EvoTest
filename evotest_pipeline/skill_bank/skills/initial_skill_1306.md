---
name: relative-property-query-result-filtering
description: When building query engine tests that verify results for relative property
  paths (e.g., child/@prop), create test trees where some nodes match with their own
  properties AND others match through descendant properties, to ensure query filtering
  doesn't produce duplicate results. This skill catches bugs where a node incorrectly
  matches a property it doesn't directly own.
code_tags:
- ORDER_DEPENDENCY
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# relative-property-query-result-filtering

## Instructions

# Relative Property Query Result Filtering

## Instructions

- WHEN the TG encounters a query engine that evaluates relative property paths (e.g., `child/@prop` in XPath or `[child/prop]` in SQL-2), THEN it should create test data where:
  1. Some nodes match the query condition through a descendant's property (e.g., node `/a/child` has `prop = "x"`)
  2. Some nodes match the query condition through their OWN property at a non-relative path (e.g., node `/b` has `prop = "x"`)
  3. The query uses the relative path syntax to explicitly reference the descendant property, NOT the direct property
  4. The expected result set should include ONLY the nodes that match via the relative path (descendant property), NOT nodes that match via direct properties

- WHEN testing relative property query conditions, THEN the test should verify that each path in the expected result set is included exactly once — no duplicates. Use `assertQuery(query, language, ImmutableList.of(...))` and the test framework will fail on size mismatch.

- WHEN a query condition uses a relative property path like `child/@prop = 'value'`, THEN the TG must ensure no node in the test tree has BOTH:
  - A direct property at the relative path's property name (e.g., `prop = "value"` on the node itself)
  - A descendant matching via the child's same property
  Because the buggy query engine may incorrectly return that node twice or match it when it shouldn't.

- Common pitfall: Only testing with nodes that have descendant properties matching the relative condition, without also creating decoy nodes that have direct (non-relative) properties with the same name that could produce false positives in query results. Always include at least one node with a direct property matching the same value, to verify the relative path filter correctly excludes it.

### Correct Example (catches the bug):
```java
// Create tree where node "two" matches via child/@prop, 
// and node "wrong" has direct @prop matching the same value
Tree c = root.getTree("/").addChild("content");
c.addChild("one").addChild("child").setProperty("prop", "aaa");
c.addChild("two").addChild("child").setProperty("prop", 
    ImmutableList.of("aaa", "bbb", "ccc"), Type.STRINGS);
c.addChild("wrong").setProperty("prop", "aaa"); // direct prop, should NOT match child/@prop
root.commit();

assertQuery("//*[(child/@prop = 'aaa')]", "xpath",
    ImmutableList.of("/content/two"));
```

### Incorrect Example (does NOT catch the bug):
```java
// Only tests nodes that DO match via descendant property
Tree c = root.getTree("/").addChild("content");
c.addChild("two").addChild("child").setProperty("prop", 
    ImmutableList.of("aaa", "bbb", "ccc"), Type.STRINGS);
root.commit();

// This passes even with the buggy code because there's no 
// distractor node with a direct @prop = 'aaa'
assertQuery("//*[(child/@prop = 'aaa')]", "xpath",
    ImmutableList.of("/content/two"));
```