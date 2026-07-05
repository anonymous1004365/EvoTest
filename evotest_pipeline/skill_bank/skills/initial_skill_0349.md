---
name: minified-resource-duplicate-detection
description: When resource references use minified name detection, test that looking
  up a non-minified resource while a minified variant exists doesn't resolve to multiple
  resources. This skill helps catch bugs where minified name discovery incorrectly
  reports minified files as available resources.
code_tags:
- RESOURCE_MANAGEMENT
test_pattern: PARAMETRIC_TEST
---

# minified-resource-duplicate-detection

## Instructions

# Minified Resource Duplicate Detection

## Instructions

WHEN the TG encounters code that resolves resource references with minified name discovery (e.g., `PackageResourceReference` using `ResourceUtils.getMinifiedName()` or checking `MIN_POSTFIX_DEFAULT_AS_EXTENSION`), THEN it should write a test that:

1. **Create a test scenario where only one resource file exists** — the non-minified version — and verify that the resource reference resolves to exactly one resource (the non-minified one).
2. **Use the exact minified naming convention** — the framework's default `.min.` infix (e.g., `a.js` exists but `a.min.js` does not; or `b.js` exists but `b.min.js` does not).
3. **Assert that the count of resolved resources is 1, not 2** — the bug causes `locate(...)` to report the minified variant as existing even when it doesn't, resulting in duplicate resource entries.

Concrete example from the actual codebase:
- The buggy `PackageResourceReference.getMinifiedName()` method checks `minifiedName.contains(MIN_POSTFIX_DEFAULT_AS_EXTENSION)` (where `MIN_POSTFIX_DEFAULT_AS_EXTENSION` is `.min.`). When a non-minified resource like `b.js` is requested but no `b.min.js` exists on disk, the buggy code incorrectly reports the minified name as available, causing two resources to be resolved instead of one.
- The test should:
  ```java
  // Correct: verify only non-minified resource is found
  PackageResourceReference ref = new PackageResourceReference(TestClass.class, "b.js");
  IResource resource = ref.getResource();
  // Assert that only one resource exists (the non-minified one)
  // This would fail on the buggy version which finds two
  ```
  
  ```java
  // WRONG: Don't test with both .min.js and .js files existing on classpath
  // That would not catch the bug because duplicates actually exist in that case
  
  // WRONG: Don't test minified name string manipulation in isolation
  // The bug is in the resource resolution pipeline, not just in getName()
  
  // WRONG: Don't assume that getMinifiedName() returning non-null means the file exists
  // The bug is precisely that getMinifiedName() returns a value that doesn't correspond to an actual file
  ```

Common pitfalls:
- **Testing only string manipulation methods in isolation** (e.g., `getMinifiedName()`) instead of testing the full resource resolution pipeline. The bug manifests when `locate()` is called with the minified name and reports success even though no file exists.
- **Setting up both .min.js and .js test resources on the classpath**, which masks the bug because duplicates would legitimately exist in that scenario.
- **Testing with resource names that don't contain `.min.` infix**, which means the minified name detection code path is never exercised.
- **Forgetting that the test needs to verify the *count* of resources returned**, not just that a resource is found. The bug manifests as finding 2 resources (minified + non-minified) when only 1 should exist.