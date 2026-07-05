---
name: plugin-realm-cache-mutation
description: Tests for caching bugs where shared mutable state in a plugin realm cache
  causes stale/wrong results between invocations. Use when testing caching logic that
  stores plugin realms per MavenProject/ClassRealm combination and mutates cached
  entries after insertion.
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
- STATE_MUTATION
- CACHING_AND_CONVERTER_REGISTRY
test_pattern: STATE_TEST
---

# plugin-realm-cache-mutation

## Instructions

# Plugin Realm Cache Mutation Checks

## Instructions

- WHEN the TG encounters a caching mechanism that stores per-project plugin realms (e.g., `Map<CacheKey, ReactorContext>` or similar `ClassRealm` cache), **and** the code mutates cached entries after they are stored (e.g., calling setters, adding artifacts, or otherwise modifying the value object after `cache.put(key, value)`),
- THEN the TG should write a test that:
  1. Executes the same cache-access path **twice** with **the same cache key** (e.g., same `MavenProject` identity, same plugin, same `ClassRealm`).
  2. After the first execution, verify that the **second execution returns the exact same cached object** (by reference) **not a fresh instance**.
  3. Verify that modifications made during the first execution (e.g., adding artifacts to the realm, resolving plugin extensions) **are visible** in the object returned by the second execution — i.e., the cache should not create a new object that loses the mutations.
- Expected behavior on the **buggy** version: the second call with the same cache key returns a **new/different instance** (different reference) that lacks the modifications from the first call, causing lost state.
- Expected behavior on the **fixed** version: the second call returns the **same instance** (same reference) and preserves all mutations from the first call.

### Common Pitfalls
- **Testing only a single cache lookup**: A single invocation cannot detect mutation-after-cache bugs. You need at least two sequential lookups with the same key.
- **Checking only value equality (equals/hashCode)**: If the cached object uses identity-based equality and the bug creates separate instances for each call, equals might still report `false` correctly. But the real bug is about **reference identity** — use `assertSame()` to verify the same object is reused across cache hits.
- **Relying solely on mock objects**: Mocking the `MavenProject` or `ClassRealm` may bypass the cache key logic. Use realistic or minimally-stubbed real objects so the cache key is computed consistently across calls.
- **Assuming the cache is query-only**: Many plugin realm caches are populated on the first call and read on subsequent calls. The bug is that the second call re-creates the realm from scratch instead of returning the cached one.

### Correct Example (conceptual)
```java
// Arrange
MavenProject project = new MavenProject(...);
Plugin plugin = new Plugin();
// set plugin coordinates
ClassRealm realm = /* obtain via the cache manager */;

// Act - first lookup (populates cache)
ReactorContext first = pluginManager.getRealm(project, plugin);
// Mutate: add artifact or resolve something
first.addArtifact(...);  // or whatever mutation happens

// Act - second lookup with same key
ReactorContext second = pluginManager.getRealm(project, plugin);

// Assert: same instance, mutations visible
assertSame(first, second);
assertTrue(second.getArtifacts().contains(...));
```

### Incorrect Example (conceptual)
```java
// Only one lookup — misses the mutation-after-cache bug
ReactorContext ctx = pluginManager.getRealm(project, plugin);
assertNotNull(ctx);

// Or: using equals instead of same
ReactorContext ctx2 = pluginManager.getRealm(project, plugin);
assertEquals(ctx, ctx2);  // WRONG: equals may pass even if different instances
```