---
name: checkpoint-max-limit-validation
description: When testing checkpoint creation methods that accept a 'max' or limit
  parameter, the TG should verify that creating checkpoints beyond the configured
  maximum causes an appropriate rejection (exception/failure), not silent truncation
  or state corruption. The test should confirm the system enforces its documented
  capacity limit for concurrent checkpoints.
code_tags:
- BOUNDARY_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# checkpoint-max-limit-validation

## Instructions

# Checkpoint Max Limit Validation

## Instructions

- WHEN the TG encounters a `checkpoint(long lifetime, Map<String,String> properties)` method in a `NodeStore` or `SegmentNodeStore` implementation that has a configurable maximum number of concurrent checkpoints (e.g., `checkpointsCacheSize`, `maxCheckpoints`, or similar limit)
- THEN the TG should write a test that:
  1. Creates exactly the maximum number of checkpoints (e.g., `maxCheckpoints`) the system allows
  2. Then attempts to create ONE MORE checkpoint beyond this limit
  3. Verifies that the extra checkpoint attempt throws a suitable exception (e.g., `CommitFailedException`, `IllegalStateException`, or returns a failure indicator) rather than silently succeeding or overwriting an existing checkpoint
- The test should NOT assume the system silently truncates or drops old checkpoints when the limit is exceeded unless that behavior is explicitly documented
- Common pitfalls to avoid:
  - Testing only with a single checkpoint and not testing boundary behavior near the maximum
  - Asserting that `null` or an empty string is returned when the system might throw an exception instead
  - Assuming the max checkpoint limit is 1 or using magic numbers without retrieving the actual configured limit via the store's configuration API
  - Failing to clean up checkpoints after the test, which could leave test state for subsequent tests
- Example of a correct test approach:
```java
// Set up store with max=5 checkpoints
SegmentNodeStore store = ...;
Map<String, String> props = Collections.emptyMap();
String[] ids = new String[5];
for (int i = 0; i < 5; i++) {
    ids[i] = store.checkpoint(60000, props);
}
// This should fail
assertThrows(SomeExpectedException.class, () -> store.checkpoint(60000, props));
```
- Example of an INCORRECT test approach (wrong):
```java
// Only checks a single checkpoint — does not test boundary
String cp = store.checkpoint(1000, new HashMap<>());
assertNotNull(cp);
// No attempt to exceed the limit
```