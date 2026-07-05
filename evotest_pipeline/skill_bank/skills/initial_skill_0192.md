---
name: pojo-reuse-extractor-state
description: ''
code_tags:
- RECURSIVE_STATE_TRACKING
- POJO_ANALYSIS_REUSE
test_pattern: STATE_TEST
---

# pojo-reuse-extractor-state

## Instructions

# Pojo Reuse Extractor Recursive State Pollution

## Instructions

- **WHEN** a `TypeExtractor` (or subclass like `PojoTypeExtractor`) is instantiated and its `analyzePojo()` or similar analysis method is called multiple times on different types, **THEN** the test must verify that each invocation produces independent results. This is because `TypeExtractor` maintains an internal `alreadySeen` (`Set<Class<?>>`) instance field that is initialized in the constructor. If the same extractor instance is reused for multiple type analyses, the `alreadySeen` set from a prior analysis may still contain classes from that prior run, causing the second analysis to incorrectly treat a new type as "already seen" (a false positive for recursive type detection), potentially resulting in truncated or incorrect `PojoTypeInfo` results.

- **WHEN** testing for this bug, **THEN** call the type extraction method **twice in sequence** on two distinct POJO types using the same extractor instance. First, analyze a simple POJO type (e.g., `MyFirstPojo.class`), then analyze a second, unrelated POJO type (e.g., `MySecondPojo.class`). Verify that the type information for the second POJO is correct and complete — specifically that it is a `PojoTypeInfo` with the expected fields. A common failure mode on the buggy version is that the second POJO analysis returns a `GenericTypeInfo` instead of a `PojoTypeInfo`, or has missing fields.

- **WHEN** constructing the test scenario, **THEN** ensure you are reusing the **same** `TypeExtractor` instance (or the same `PojoTypeExtractor` instance created via `AvroTypeInfo`'s private inner class). A clean test should mirror the pattern found in `AvroTypeInfo` where a single `PojoTypeExtractor` is created once and used for a single type. To expose the bug, create a test where the extractor is used for a **first** type, then used again for a **second** type. Without this skill, a test might only test a single type extraction in isolation, missing the cross-invocation state pollution.

- **WHEN** verifying type correctness, **THEN** assert that the second type extraction returns a `PojoTypeInfo` (not `GenericTypeInfo`), and that its `getTypeClass()` returns the expected class. On the buggy version, the second call may incorrectly return a `GenericTypeInfo` because the `alreadySeen` set from the first analysis still contains classes, causing the second analysis to prematurely stop.

- **Common pitfall**: Testing only a single type extraction per `TypeExtractor` instance. This hides the bug because each fresh extractor has a fresh `alreadySeen` set. The bug only manifests when the extractor instance is **reused**. Also, avoid assuming that just because the `TypeExtractor` is created each time in production code (like `AvroTypeInfo`), that a reused instance is safe — the risk is in scenarios where extraction is called multiple times on the same instance.

### Correct approach (exposes the bug):
```java
// Reuse the same TypeExtractor instance for two different POJO types
TypeExtractor extractor = new TypeExtractor();
TypeInformation<?> firstType = extractor.analyzePojo(FirstPojo.class, ...);
TypeInformation<?> secondType = extractor.analyzePojo(SecondPojo.class, ...);

// This assertion may fail on the buggy version (second extract returns GenericTypeInfo)
assertTrue("Second POJO should be recognized as PojoTypeInfo", 
    secondType instanceof PojoTypeInfo);
assertEquals(SecondPojo.class, secondType.getTypeClass());
```

### Incorrect approach (misses the bug):
```java
// Each extraction uses a fresh extractor — bug never manifests
TypeInformation<?> firstType = new TypeExtractor().analyzePojo(FirstPojo.class, ...);
TypeInformation<?> secondType = new TypeExtractor().analyzePojo(SecondPojo.class, ...);
// Both pass even on buggy version because each has its own alreadySeen set
assertTrue(secondType instanceof PojoTypeInfo);
```