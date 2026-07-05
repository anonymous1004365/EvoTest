---
name: per-lookup-wagon-instantiation-testing
description: Teaches how to test that Plexus per-lookup (prototype-scoped) components
  like Wagon are freshly instantiated on each lookup, avoiding reuse of stale state
  across calls.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- STATE_MUTATION
- CACHING_AND_CONVERTER_REGISTRY
test_pattern: STATE_TEST
---

# per-lookup-wagon-instantiation-testing

## Instructions

# Per-Lookup Wagon Instantiation Testing

## Instructions

- WHEN the code handles Plexus/Plexus-container lookups for `Wagon` implementations with a `per-lookup` (prototype) component lifecycle
- THEN write a state test that:
  1. Obtains a Wagon instance via `DefaultWagonManager.getWagon(Repository)` or `container.lookup(Wagon.class, hint)`
  2. Calls a mutating method on it (e.g., `getFile()` which changes internal state)
  3. Performs a second lookup for the same protocol/hint
  4. Calls the same mutating method on the second instance
  5. Asserts that the state of the second instance is **independent** of the first instance (i.e., each lookup returns a fresh instance with default/initial state)
- The test should verify that shared or static fields, or instance-level caches, are not unintentionally reused across per-lookup instantiations
- For example, if a `PerLookupWagon` accumulates results in a `List<String> getResults()`, the test should:
  - First lookup → call mutating method → verify result contains expected item(s)
  - Second lookup → call same mutating method → verify result contains ONLY the item(s) from the second call, NOT items from the first call
- **Common pitfall**: Testing only that a single instance works correctly, without verifying that separate lookups produce independent instances. Also, failing to call a state-mutating method on each fresh instance before comparing state.
- **Correct example**:
```java
Wagon w1 = wagonManager.getWagon(repository);
w1.getFile(repository, artifact, transferListener, null);
List<String> results1 = ((PerLookupWagon) w1).getResults();
assertThat(results1).containsExactly("file1");

Wagon w2 = wagonManager.getWagon(repository);
w2.getFile(repository, artifact, transferListener, null);
List<String> results2 = ((PerLookupWagon) w2).getResults();
assertThat(results2).containsExactly("file2"); // NOT "file1" + "file2"
```

- **Incorrect example**:
```java
Wagon w1 = wagonManager.getWagon(repository);
assertNotNull(w1); // Only checks non-null, not independence
Wagon w2 = wagonManager.getWagon(repository);
assertNotSame(w1, w2); // Checks different objects but not state isolation
```