---
name: shell-setiter-iterator-name-parameter
description: When testing shell commands that accept iterator class names and options,
  the TG should verify that parameter parsing correctly handles absent/non-existent
  options as well as valid ones, catching IllegalArgumentException for missing required
  parameters.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# shell-setiter-iterator-name-parameter

## Instructions

# Shell setiter Iterator Name Parameter Validation

## Instructions

- WHEN the TG encounters a shell command test that invokes `setiter` (or similar shell commands that accept class names and optional parameters via `-p` flags)
- THEN the TG should write a test that:
  1. Invokes the shell command `setiter -class <ClassName> -p <optionNumber>` with a valid iterator class like `VersioningIterator` and a numeric parameter like `1` (without parentheses)
  2. Invokes the same command with a non-existent/random class name like `o.a.a.foo` to verify proper error handling
  3. Crucially, invokes the command **without** the required `-p` option (e.g., just `setiter -class VersioningIterator`) to verify that an `IllegalArgumentException` is thrown when a required parameter is missing
  4. The test should also verify that commands with the correct `-p` syntax but with extra/incorrect characters (like parentheses around the value) similarly trigger `IllegalArgumentException`

- Common pitfalls to avoid:
  - Testing only valid parameter formats without checking error cases for missing required options
  - Forgetting to test the edge case where `-p` is completely absent (the command should still fail with a clear exception)
  - Assuming that a missing `-p` option silently defaults to some value instead of throwing
  - Testing only String type parameters when numeric parameters (via `-p`) are also relevant

- Concrete example (correct approach):
  ```java
  // Test that setiter with -p option works
  ts.exec("setiter -class VersioningIterator -p 1", false, new Result(2, true));
  
  // Test that setiter with non-existent class works (different error path)
  ts.exec("setiter -class o.a.a.foo -p 1", false, new Result(2, true));
  
  // Test that setiter WITHOUT -p option throws IllegalArgumentException
  ts.exec("setiter -class VersioningIterator", false, new Result(2, false));
  
  // Test that setiter with parenthesized -p option throws IllegalArgumentException
  ts.exec("setiter -class VersioningIterator -p 1(..)", false, new Result(2, false));
  ```

- Concrete example (wrong approach that misses the bug):
  ```java
  // BAD: Only tests valid parameters, misses missing -p case
  ts.exec("setiter -class VersioningIterator -p 1", false, new Result(2, true));
  // BAD: Doesn't test the bare class without -p
  ```