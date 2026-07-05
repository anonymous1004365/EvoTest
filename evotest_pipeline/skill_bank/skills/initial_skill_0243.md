---
name: thread-pool-profile-clone-field-mismatch
description: When a class overrides clone() but incorrectly maps fields (e.g., sets
  poolSize to the value of maxPoolSize), tests should verify clone preserves independent
  field values. Apply when a Cloneable class has a manual clone() implementation with
  field assignments.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# thread-pool-profile-clone-field-mismatch

## Instructions

# Thread Pool Profile Clone Field Mapping Verification

## Instructions

- WHEN the TG encounters a class that implements `Cloneable` and overrides `clone()` with manual field-by-field assignments (like `ThreadPoolProfile.clone()`)
- THEN it should write a test that:
  1. Creates an instance of the class (e.g., `ThreadPoolProfile`)
  2. Sets **distinct, non-null values** for every mutable field, paying special attention to fields with similar names or types (e.g., `poolSize` vs `maxPoolSize`, both `Integer`)
  3. Calls `clone()` on the original instance
  4. Asserts that each field on the cloned object **exactly matches** the corresponding field value on the original
  5. The assertion must use `assertEquals(expected, actual)` with the original's getter value as expected — this detects bugs where `clone()` mistakenly copies `maxPoolSize` into `poolSize`

- Common pitfalls to avoid:
  - ❌ Setting `poolSize` to the same value as `maxPoolSize` — this hides the bug since `clone()` sets `poolSize = maxPoolSize` in the buggy version
  - ❌ Only testing a subset of fields — the bug was specifically in the `poolSize` / `maxPoolSize` pair; test ALL numeric fields independently
  - ❌ Not using `getPoolSize()` to verify — the clone bug sets `poolSize` to `maxPoolSize` value on the clone, breaking the intended copy semantics

- ✅ Correct approach example:
```java
ThreadPoolProfile profile = new ThreadPoolProfile("custom");
profile.setPoolSize(5);          // distinct from maxPoolSize
profile.setMaxPoolSize(15);      // distinct from poolSize
profile.setKeepAliveTime(25L);
profile.setMaxQueueSize(250);
profile.setAllowCoreThreadTimeOut(true);
profile.setRejectedPolicy(ThreadPoolRejectedPolicy.Abort);

ThreadPoolProfile clone = profile.clone();

assertEquals(Integer.valueOf(5), clone.getPoolSize());       // Would fail on buggy version (clone sets poolSize=maxPoolSize)
assertEquals(Integer.valueOf(15), clone.getMaxPoolSize());
assertEquals(Long.valueOf(25), clone.getKeepAliveTime());
assertEquals(Integer.valueOf(250), clone.getMaxQueueSize());
assertEquals(Boolean.TRUE, clone.getAllowCoreThreadTimeOut());
assertEquals(ThreadPoolRejectedPolicy.Abort, clone.getRejectedPolicy());
```

- ❌ Buggy approach (does NOT catch the bug):
```java
profile.setPoolSize(15);   // same as maxPoolSize=15 — test passes even when buggy!
profile.setMaxPoolSize(15);
// clone.getPoolSize() returns 15 in both buggy and fixed versions — test passes either way
```