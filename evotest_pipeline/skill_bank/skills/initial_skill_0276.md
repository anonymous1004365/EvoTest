---
name: concurrent-path-argument-validation
description: WHEN a method builds paths or parent paths from user-supplied arguments
  in a multithreaded context AND validates the resulting path string, THEN the TG
  should test with concurrent calls using path-derived arguments that could produce
  edge-case path values like "/" or empty strings. This skill catches race conditions
  where path validation logic fails under concurrent execution.
code_tags:
- CONCURRENCY
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# concurrent-path-argument-validation

## Instructions

# Concurrent Path Argument Validation

## Instructions

WHEN a method takes a string argument (e.g., a repository path), builds a derived path from it (e.g., a parent path or sub-path), and validates that derived path — and this method can be called from multiple threads concurrently — THEN the TG should:

1. **Identify the path-construction logic.** Look for code that transforms an input path string into a derived path (e.g., removing a trailing slash, extracting the parent, concatenating with a prefix like `"/"`).

2. **Identify edge-case inputs that produce boundary paths.** In particular, look for inputs that, when transformed, yield paths like:
   - `"/"` (root path)
   - `""` (empty string)
   - Paths with only special characters

3. **Write a concurrent test that drives multiple threads**, each thread calling the method with these edge-case inputs repeatedly. For example, if the method derives a parent path from `childPath`, test with `childPath = "/"` or `childPath = ""` or `childPath = "<prefix>/"` where removing the last segment yields root.

4. **Verify that no `IllegalArgumentException` or other unexpected exception is thrown** when the method is called from multiple threads with these inputs. The test should pass on the fixed version but fail (throwing `IllegalArgumentException` with a message like `"-/<somepath>"`) on the buggy version.

5. **Common pitfalls to avoid:**
   - Testing only single-threaded path validation — concurrent execution can change the interleaving of path operations.
   - Testing only with "normal" paths like `"/a/b/c"` — the bug is triggered only by edge-case paths where the derived path is `"/"`.
   - Not using `ExecutorService` with `CountDownLatch` or `CyclicBarrier` to ensure threads run concurrently.
   - Forgetting to catch or assert on the specific exception class (e.g., `IllegalArgumentException`).

**Correct example:**

A `ConcurrentWriteTest` that:
- Creates a path variable like `"/org.apache.jackrabbit.mk.ConcurrentWriteTest"`
- Passes it to a method that derives a parent path (e.g., by finding the last `"/"` and taking the substring before it)
- Calls that method from multiple concurrent threads
- Expects no exception

**Incorrect approach:**

A single-threaded test that only checks normal paths like `"/a/b/c"` for valid parent path derivation, missing the edge case where the path is just a single segment under root and the derived parent becomes `"/"`.