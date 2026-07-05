---
name: checkpoint-retrieval-null-handling
description: When implementing a retrieve() method that looks up stored state by an
  identifier key, ensure it returns null for non-existent keys rather than throwing
  an exception or returning garbage. This skill helps detect missing null-guards on
  lookup operations over maps/collections.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# checkpoint-retrieval-null-handling

## Instructions

# Checkpoint Retrieval Null Handling

## Instructions

- WHEN the TG encounters a method named `retrieve` (or similar lookup-by-key method) on a `NodeStore`-like interface that is supposed to return a stored checkpoint/node state by a given checkpoint ID string
- THEN the TG should write a test that calls the retrieve method with a **non-existent checkpoint ID** (e.g., `"nonExistentCheckpoint"` or an ID that was never created) and verify that the return value is **null** (the method should NOT throw an exception or return a non-null stale value)
- Include concrete verification: `assertNull(store.retrieve("nonExistentCheckpoint"))` on the buggy version would either throw or return non-null; on the fixed version it returns null
- **Common pitfalls**: 
  - Testing only with valid checkpoint IDs that exist (does not exercise the null-returning path)
  - Assuming a Map's `.get(key)` call always handles missing keys gracefully — some implementations may throw or have side effects
  - Not checking the method contract for what happens when the ID doesn't exist
  - Testing only the `checkpoint()` + `retrieve()` round-trip (happy path) without testing the lookup-for-non-existent-keys edge case

### Correct approach example:
```java
// Given a NodeStore that has NO checkpoints created yet
NodeStore store = new MemoryNodeStore();

// When retrieving with a non-existent checkpoint ID
NodeState result = store.retrieve("nonExistentId");

// Then it should return null (not throw an exception)
assertNull("Retrieve should return null for missing checkpoint", result);
```

### Incorrect approach example:
```java
// ❌ Only testing the happy path — missing checkpoints never exercised
String cp = store.checkpoint(...);
assertNotNull(store.retrieve(cp));

// ❌ Not verifying the null case at all for a separate store instance
```