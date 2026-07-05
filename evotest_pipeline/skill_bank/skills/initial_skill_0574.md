---
name: exotic-classloader-type-compatibility
description: When a custom ClassLoader returns incompatible types (e.g. objects not
  castable to String or CtTypeReference), the test should verify that the compiler
  handles such exotic types gracefully without throwing false-positive compilation
  errors. This skill applies to scenarios where class loading and reflection may produce
  unexpected type mismatches.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- NULL_CHECK
- CLASS_LOADING_AND_REFLECTION
test_pattern: EXCEPTION_TEST
---

# exotic-classloader-type-compatibility

## Instructions

# Exotic ClassLoader Type Compatibility

## Instructions

- WHEN the TG encounters code that uses a custom ClassLoader to load classes, interfaces, or types, and those loaded types may not conform to expected Java type hierarchies (e.g., a `ClassLoader` returns an object of a type that is not assignable to `String` or `CtTypeReference`, or returns `null` for a non-existent type)
- THEN the TG should write a test that:
  1. Creates an instance of the custom ClassLoader (e.g., `ExoticClassLoader`)
  2. Loads a class or type using that ClassLoader where the loaded type is deliberately incompatible or exotic (e.g., a `String` when a `CtTypeReference` is expected, or a completely unrelated class)
  3. Passes that type to the method under test and expects that no exception is thrown, or that the method gracefully handles the incompatibility
  4. Verifies that the compilation succeeds without `ClassCastException`, `NullPointerException`, or other spurious runtime errors

- The TG should verify that the method under test correctly handles types loaded by exotic ClassLoaders, including:
  - Types that are assignment-incompatible with expected interfaces
  - Null types (if the ClassLoader returns null for a missing class)
  - Primitive types if applicable

- **Common pitfalls to avoid:**
  - Assuming all ClassLoaders return types that implement the expected interfaces (e.g., `CtTypeReference`)
  - Not testing with a custom ClassLoader that returns unexpected/unrelated types
  - Testing only with the default ClassLoader or normal class loading scenarios
  - Forgetting that the method should not throw `ClassCastException` or fail compilation when encountering exotic types

- **Correct example:**
  ```java
  // Given a Launcher with an ExoticClassLoader that returns String where a type is expected
  Launcher launcher = new Launcher();
  ExoticClassLoader exoticLoader = new ExoticClassLoader();
  launcher.setClassLoader(exoticLoader);
  // The test should verify that building the model or compiling succeeds
  // even when the ClassLoader returns incompatible types
  assertDoesNotThrow(() -> {
      launcher.buildModel();
  });
  ```

- **Incorrect example (common pitfall):**
  ```java
  // Only testing with the default class loader - misses the bug
  Launcher launcher = new Launcher();
  launcher.buildModel(); // Works fine with default loader
  // But fails with ExoticClassLoader due to ClassCastException
  ```