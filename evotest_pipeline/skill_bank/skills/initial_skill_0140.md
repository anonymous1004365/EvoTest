---
name: garbage-collection-path-validation
description: WHEN the TG encounters path parsing/validation in GarbageCollectionAlgorithm.makeRelative(),
  THEN it should test malformed paths that trigger IllegalArgumentException, covering
  short paths (<2 tokens), missing colons in long paths, and paths with unexpected
  token counts after TABLE_DIR stripping.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# garbage-collection-path-validation

## Instructions

# Garbage Collection Path Validation

## Instructions

- WHEN the TG encounters the `GarbageCollectionAlgorithm.makeRelative(String path, int expectedLen)` method — a private method that parses and validates file/directory paths for garbage collection — THEN it should write unit tests that verify `IllegalArgumentException` is thrown for malformed paths.

- The method `makeRelative(String path, int expectedLen)` accepts a `String path` and an `int expectedLen` (0, 2, or 3). It normalizes the path (strips leading "../", trailing/leading "/", collapses empty tokens from "//"), then splits on "/". The validation logic is:

  1. **Long path (tokens.length > 3):** If the path does NOT contain ":", throw IllegalArgumentException. Otherwise, check the position of `ServerConstants.TABLE_DIR` (usually "tables"):
     - If 4th-from-last token is TABLE_DIR AND expectedLen is 0 or 3: accept (relPath = last 3 tokens)
     - If 3rd-from-last token is TABLE_DIR AND expectedLen is 0 or 2: accept (relPath = last 2 tokens)
     - Otherwise: throw IllegalArgumentException

  2. **Medium path (tokens.length == 3):** Accept if expectedLen is 0 or 3, otherwise throw IllegalArgumentException.

  3. **Short path (tokens.length == 2):** Accept if expectedLen is 0 or 2, otherwise throw IllegalArgumentException.

  4. **Very short path (tokens.length < 2):** Always throw IllegalArgumentException.

- THEN the TG should test with at least these malformed inputs that exercise each rejection branch:

  - **Short paths with wrong expectedLen:** `makeRelative("a/b", 3)` — tokens.length == 2, expectedLen is 3 (not 0 or 2) → IllegalArgumentException
  - **Medium paths with wrong expectedLen:** `makeRelative("a/b/c", 2)` — tokens.length == 3, expectedLen is 2 (not 0 or 3) → IllegalArgumentException
  - **Long path without colon:** `makeRelative("hdfsfoo6000accumulotables4t0F000rf", 0)` — tokens.length > 3 and no ":" → IllegalArgumentException (path does not contain ":")
  - **Long path with colon but wrong TABLE_DIR position:** `makeRelative("hdfs://foo:6000/accumulo/other/4/t0/F000.rf", 0)` — tokens.length > 3, contains ":", but the token before `t0` is not TABLE_DIR at the expected position → IllegalArgumentException (the fix in this bug changed behavior for this case)
  - **Very short path:** `makeRelative("a", 0)` — tokens.length < 2 → IllegalArgumentException
  - **Single token with slash:** `makeRelative("/a", 0)` — after stripping leading "/", tokens.length == 1 < 2 → IllegalArgumentException

- **Common pitfalls to avoid:**
  - **NOT** testing paths with fewer than 2 tokens — these always throw but are easy to miss.
  - **NOT** testing expectedLen mismatch scenarios (e.g., path with 3 tokens but expectedLen=2).
  - Testing only happy-path paths like `"hdfs://foo:6000/accumulo/tables/4/t0/F000.rf"` with expectedLen=0, which succeeds. The bug manifests as an unhandled IllegalArgumentException for unexpected path formats.
  - Assuming the `makeRelative` method is unreachable via public API — it IS called from `confirmDeletes()` with expectedLen=3 for references and expectedLen=2 for bulk processing flags (`blipPath`), and from `makeRelative(Collection)` with expectedLen=0 for candidates. Any malformed path from those callers will crash the GC.

- **Correct test approach** (using `GarbageCollectionAlgorithm` directly as the class is package-private in `org.apache.accumulo.gc`):

```java
// Correct: test IllegalArgumentException for short path with wrong expectedLen
GarbageCollectionAlgorithm gca = new GarbageCollectionAlgorithm();
// Use reflection or a package-level test to access makeRelative
// The test should verify IllegalArgumentException is thrown
try {
  // invoke makeRelative("a/b", 3) via reflection
  Assert.fail("Expected IllegalArgumentException");
} catch (IllegalArgumentException e) {
  // expected
}

// Correct: test for long path without colon
try {
  // invoke makeRelative("hdfsfoo6000accumulotables4t0F000rf", 0) via reflection
  Assert.fail("Expected IllegalArgumentException");
} catch (IllegalArgumentException e) {
  // expected
}
```

- **Incorrect test approach** (insufficient coverage):

```java
// WRONG: Only testing valid paths — misses the bug entirely
gce.candidates.add("hdfs://foo:6000/accumulo/tables/4/t0/F000.rf");
gca.collect(gce); // works fine, no exception

// WRONG: Testing with a "bad" path that doesn't actually trigger the bug
gce.candidates.add("/4/t0/F000.rf"); // this is valid (3 tokens, expectedLen=0)
```

- The triggering test `testBadDeletes()` adds a candidate that is a URI-style path without a proper `tables` directory structure. The `makeRelative` call with expectedLen=0 receives a path like `"hdfs://foo:6000/accumulo/other/4/t0/F000.rf"` — tokens.length > 3, contains ":", but `tokens[tokens.length-4]` is not TABLE_DIR and `tokens[tokens.length-3]` is not TABLE_DIR at the expected offset, so it throws IllegalArgumentException. The test should verify this exception is thrown rather than silently producing wrong output.