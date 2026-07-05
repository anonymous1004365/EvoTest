---
name: node-state-map-hidden-value-handling
description: When extracting values from a NodeState map, hidden properties (starting
  with ':') may be returned even when the map appears to contain only user-defined
  keys. Tests should verify that only expected non-hidden values are returned and
  that hidden values do not leak into the result.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# node-state-map-hidden-value-handling

## Instructions

# NodeState Hidden Value Handling

## Instructions

- WHEN the code under test calls `NodeState.getKeys()` or iterates over NodeState properties and uses a filtering mechanism (e.g., check for `:` prefix to identify hidden properties)
- THEN the TG should verify that hidden properties (keys starting with `:`) are correctly excluded from the result. Create a NodeState that contains BOTH normal properties AND hidden properties (prefixed with `:`). Assert that the returned map contains only the expected normal keys and values, and does NOT include the hidden keys/values. Also verify that if no hidden properties exist, the behavior is unchanged.
- Include a test where a hidden property (e.g., `:hiddenKey` with value `hiddenValue`) is set alongside a normal property (e.g., `normalKey` with value `normalValue`). The expected result should be a map containing only `{normalKey=normalValue}` — NOT containing `:hiddenKey`.
- Common pitfalls: (1) Testing only with normal keys and not including any hidden `:`-prefixed keys, thus missing the bug. (2) Assuming `getKeys()` automatically filters hidden properties — it does not; the filtering must be applied explicitly in the conversion logic. (3) Not verifying the negative case — that hidden values are absent from the result map.

### Correct example

```java
// Setup: Create a NodeState with both normal and hidden properties
NodeBuilder nb = new NodeBuilder();
nb.setProperty("normalKey", "normalValue");
nb.setProperty(":hiddenKey", "hiddenValue"); // hidden property
NodeState state = nb.getNodeState();

Map<String, String> result = factory.convertNodeState(state);

// Verify only non-hidden properties are present
assertNotNull(result.get("normalKey"));
assertEquals("normalValue", result.get("normalKey"));
assertNull("Hidden property should not be included", result.get(":hiddenKey"));
```

### Incorrect example

```java
// BUGGY: Only testing with normal keys, never adding hidden properties
NodeBuilder nb = new NodeBuilder();
nb.setProperty("normalKey", "normalValue");
NodeState state = nb.getNodeState();

Map<String, String> result = factory.convertNodeState(state);

// This passes even on buggy code, missing the regression
assertEquals("normalValue", result.get("normalKey"));
assertEquals(1, result.size());
```

### Failure expectation

On the buggy version, the test fails with a message like:
```
expected null, but was:<hiddenValue>
```
when asserting `assertNull(result.get(":hiddenKey"))` — indicating the hidden property leaked into the result map.