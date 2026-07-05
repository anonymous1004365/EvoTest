---
name: missing-equals-hashcode-config-class
description: ''
code_tags:
- STATE_MUTATION
- CACHING_KEY_EQUALS_HASHCODE
test_pattern: STATE_TEST
---

# missing-equals-hashcode-config-class

## Instructions

# Missing equals()/hashCode() on Config/State Class

## Instructions

WHEN the TG encounters a class that:
- Holds mutable configuration/state fields (e.g., `BatchWriterConfig` with fields like `maxMemory`, `maxLatency`, `timeout`, `maxWriteThreads`, `durability`)
- Has setter methods that return `this` for chaining
- Implements `Writable` (or any serialization interface) — a strong signal that the object may be compared or used as a key
- Does NOT override `equals(Object)` and `hashCode()` from `Object`

THEN the TG should:
1. Write a test that creates **two default-constructed instances** (no setters called) and asserts they are equal via `assertEquals(instance1, instance2)`.
2. Write a test that asserts `assertEquals(instance1.hashCode(), instance2.hashCode())` to verify hash consistency.
3. Write a test that mutates one field (e.g., `setMaxMemory(1)`) and verifies the instances are now NOT equal via `assertNotEquals(instance1, instance2)`.
4. Write a test that sets equivalent values via different setters (e.g., `setMaxLatency(10, TimeUnit.SECONDS)` vs `setMaxLatency(10000, TimeUnit.MILLISECONDS)`) and asserts equality.

**What to expect on the buggy version:**
- Two default-constructed instances will have different `toString()` representations (e.g., `@37073255` vs `@397986ac`) and fail `assertEquals()` because the default `Object.equals()` uses reference identity.
- The test failure message will show different `@hex` hashcodes.

**Common pitfalls to avoid:**
- ❌ Testing only setter/getter behavior without verifying object identity/equality semantics
- ❌ Assuming default `Object.equals()` is sufficient for value comparison
- ❌ Only testing with non-default values and missing the default-vs-default equality case
- ❌ Not testing `hashCode()` consistency alongside `equals()`

### Correct Test Pattern (for BatchWriterConfig-like classes):
```java
// Two default-constructed instances MUST be equal
BatchWriterConfig cfg1 = new BatchWriterConfig(), cfg2 = new BatchWriterConfig();
assertEquals(cfg1, cfg2);
assertEquals(cfg1.hashCode(), cfg2.hashCode());

// After mutation, they MUST NOT be equal
cfg2.setMaxMemory(1);
assertNotEquals(cfg1, cfg2);

// Equivalent values via different setters MUST be equal
cfg1 = new BatchWriterConfig();
cfg2 = new BatchWriterConfig();
cfg1.setMaxLatency(10, TimeUnit.SECONDS);
cfg2.setMaxLatency(10000, TimeUnit.MILLISECONDS);
cfg1.setMaxMemory(100);
cfg2.setMaxMemory(100);
cfg1.setTimeout(10, TimeUnit.SECONDS);
cfg2.setTimeout(10000, TimeUnit.MILLISECONDS);
assertEquals(cfg1, cfg2);
assertEquals(cfg1.hashCode(), cfg2.hashCode());
```

### Incorrect Test Pattern (missing the bug):
```java
// ❌ Only tests getter values, not equality
BatchWriterConfig bwConfig = new BatchWriterConfig();
assertEquals(50 * 1024 * 1024l, bwConfig.getMaxMemory());

// ❌ Never checks that two default instances are equal
// ❌ Never checks hashCode consistency
```