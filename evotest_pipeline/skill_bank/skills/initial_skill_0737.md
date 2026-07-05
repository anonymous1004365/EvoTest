---
name: lazy-type-description-resolution-testing
description: Learn how to test type description resolution in type pools when lazy
  resolution is enabled. Use this when testing TypePool.Default with LazyResolution
  to verify that non-enclosed anonymous types resolve correctly without errors.
code_tags:
- NULL_CHECK
- VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: PARAMETRIC_TEST
---

# lazy-type-description-resolution-testing

## Instructions

# Lazy Type Description Resolution Testing

## Instructions

**WHEN** the TG encounters a `TypePool.Default` with lazy resolution enabled (e.g., `TypePool.Default.WithLazyResolution`), and there is logic that creates or looks up type descriptions for anonymous classes that are NOT enclosed by a known outer class:

**THEN** the TG should write a test that:
1. Creates a `TypePool.Default.WithLazyResolution` instance (or equivalent lazy-resolving type pool).
2. Attempts to describe (look up) a non-enclosed anonymous type name — for example, a type name with a `$` suffix but no enclosing class prefix, or a synthetic anonymous type that lacks a proper outer class.
3. Calls `describe(typeName)` or similar resolution method on the type pool.
4. Verifies that the resolution completes successfully (no `NullPointerException`, no `IllegalArgumentException`) and returns a valid `TypeDescription` or `TypeDescription.Generic` that is not null.

**CRITICAL — Common pitfalls to avoid:**
- ❌ Do NOT test only with named/enclosed classes — anonymous types may have different resolution paths.
- ❌ Do NOT assume that all type resolutions succeed with the same `resolve()` call pattern — lazy resolution may defer computation and fail later during `describe()`.
- ❌ Do NOT forget that `WithLazyResolution` wraps type descriptions lazily; the error may manifest not during pool creation but during the `describe()` call.
- ❌ Do NOT test only with a non-lazy `TypePool.Default` — lazy resolution is the root cause.
- ❌ Do NOT test with null input — the bug is specifically about a valid type name that triggers a failure in lazy resolution.

**Correct test example (detects bug):**
```java
@Test
public void testNonEnclosedAnonymousType() {
    TypePool typePool = TypePool.Default.WithLazyResolution.ofClassPath();
    // Non-enclosed anonymous type name (no enclosing class)
    TypeDescription typeDescription = typePool.describe("some.package.SomeClass$1").resolve();
    assertNotNull(typeDescription);
    // Further assertions on the resolved type
}
```

**Incorrect test (misses bug — testing non-lazy pool):**
```java
@Test
public void testNonEnclosedAnonymousType() {
    TypePool typePool = TypePool.Default.ofClassPath();
    TypeDescription typeDescription = typePool.describe("some.package.SomeClass$1").resolve();
    assertNotNull(typeDescription);
}
```

**What to expect on the buggy version:** A `NullPointerException` or `IllegalStateException` during the `describe()` or `resolve()` call, caused by the lazy resolution path failing to find an enclosing class for the anonymous type.