---
name: cost-estimation-null-property-value
description: When testing cost estimation for index queries with null PropertyValue,
  validate that the cost is finite and reasonable rather than zero or INFINITY, because
  null values may bypass pattern-based encoding and result in incorrect cost calculations.
code_tags:
- NULL_CHECK
- ITERATION_TRANSFORM
- COST_ESTIMATION
- INDEX_QUERY
test_pattern: PARAMETRIC_TEST
---

# cost-estimation-null-property-value

## Instructions

# Cost Estimation with Null Property Value

## Instructions

- WHEN the TG encounters a `getCost(Filter, String, PropertyValue)` method on a `PropertyIndexLookup` (or similar index lookup class) that internally uses `encode(value, pattern)` and passes the result to `s.count(...)` 
- THEN the TG should verify the method handles a `null` PropertyValue argument correctly by:
  - Writing a test that calls `lookup.getCost(filter, "someProperty", null)` 
  - Asserting that the returned cost is a reasonable finite value (e.g., `cost >= MANY` where MANY is the total entry count), NOT `0.0` and NOT `Double.POSITIVE_INFINITY`
  - The test should first add at least 100 indexed entries with diverse values (e.g., `"x" + i % 20`), configure the index definition with `entryCount = -1`, and then query with `null` as the PropertyValue argument

- Common pitfalls to avoid:
  - Testing only non-null PropertyValue arguments (single value and multi-value) while ignoring the null case
  - Asserting that cost is `0.0` or `Double.POSITIVE_INFINITY` — the cost should be a finite value >= the total number of entries
  - Using a mock or stub for `PropertyIndexLookup` rather than setting up a real indexed NodeState through the EditorHook
  - Forgetting to disable entry count estimation (`index.setProperty("entryCount", -1)`) so the cost is computed from actual index traversal

- Example of correct test structure:
```java
NodeState root = INITIAL_CONTENT;
NodeBuilder builder = root.builder();
NodeBuilder index = createIndexDefinition(
    builder.child(INDEX_DEFINITIONS_NAME), "foo",
    true, false, ImmutableSet.of("foo"), null);
index.setProperty("entryCount", -1);
NodeState before = builder.getNodeState();

for (int i = 0; i < MANY; i++) {
    builder.child("n" + i).setProperty("foo", "x" + i % 20);
}
NodeState after = builder.getNodeState();
NodeState indexed = HOOK.processCommit(before, after, CommitInfo.EMPTY);

FilterImpl f = createFilter(indexed, NT_BASE);
PropertyIndexLookup lookup = new PropertyIndexLookup(indexed);

double cost = lookup.getCost(f, "foo", null);
assertTrue("cost: " + cost, cost >= MANY);  // cost should be >= total entries
```

- Example of buggy (incorrect) test that would miss the bug:
```java
// Only tests non-null values — does NOT test null
cost = lookup.getCost(f, "foo", PropertyValues.newString("x1"));
assertTrue("cost: " + cost, cost >= 6.5 && cost <= 7.5);
// Missing: cost = lookup.getCost(f, "foo", null);
```