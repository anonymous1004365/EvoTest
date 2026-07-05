---
name: reactive-command-output-type-resolution
description: When resolving output types for reactive command segments, the test generator
  should verify that both raw Class types and generic CtTypeReference types are correctly
  handled when determining streaming vs non-streaming output, and that no NullPointerException
  occurs when the resolved Java type is null.
code_tags:
- VALIDATION
- NULL_CHECK
- ARGUMENT_VALIDATION
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# reactive-command-output-type-resolution

## Instructions

# Reactive Command Output Type Resolution

## Instructions

**WHEN** the Test Generator (TG) encounters a method that resolves or determines the output type of a reactive command (e.g., checking if a return type is a "streaming" type like `Flux` or `Observable`), and the resolution logic handles both `java.lang.reflect.Type` and `CtTypeReference`-based type information:

- **THEN** the TG should write a test that:
  1. Invokes the type-resolution method with a concrete return type that is **not** a streaming type (e.g., `String.class` or `Void.class` for a `Mono<String>` / `Mono<Void>` / single-value response).
  2. Invokes the same method with a **generic** type that resolves to a **non-streaming** type (e.g., a `CtTypeReference` wrapping `String`).
  3. Verifies the method returns the correct output type indicator (e.g., a non-streaming flag, or no exception thrown) for **both** cases.
  4. Verifies that the method does **not** throw a `NullPointerException` when the underlying Java type resolution returns `null` for a `CtTypeReference`-based type.

- **WHEN** the method converts a `CtTypeReference` to its backing `Class` via a helper like `getJavaType()` or `getActualJavaType()`:
  - **THEN** the TG **must** test with a type whose `getJavaType()` or equivalent returns `null` — the method should handle this gracefully (e.g., default to `Object.class` or skip the type).

- **Common pitfalls to avoid:**
  - ❌ Testing only with raw `Class` types (e.g., `String.class`) while ignoring `CtTypeReference` / generic type inputs.
  - ❌ Assuming that `getJavaType()` on a `CtTypeReference` never returns `null`.
  - ❌ Not testing both streaming and non-streaming output paths when the code conditionally branches on the resolved type.
  - ❌ Writing a test that only exercises the success path; the fix was specifically for a crash (NPE) on non-entity types.

- **Correct example (conceptual):**
  ```
  // Given a method: CommandSegmentCommandOutputFactory.resolveDefinedOutput(ParameterBinderSession)
  // Test that it can handle both:
  //   - Mono<String> (raw Class: String.class) → non-streaming output, no crash
  //   - Mono<Void> (via CtTypeReference) → non-streaming output, no crash
  
  ReactiveCommandSegmentCommandFactory factory = new ReactiveCommandSegmentCommandFactory(method,…
  // Use a method returning Mono<Void> or Mono<String>
  // Trigger resolution via ReactiveCommandSegmentCommandFactory.create
  // Assert no exception is thrown
  
  actualResult = factory.create(…);
  // Assert that the result command's output is correctly resolved as non-streaming
  ```

- **Incorrect example (misses the bug):**
  ```
  // ❌ Only tests with a raw java.lang.reflect.Type, doesn't exercise CtTypeReference path
  // This would NOT catch the NullPointerException bug
  
  factory = new ReactiveCommandSegmentCommandFactory(methodReturningMonoOfString, …);
  result = factory.create(session);
  // The bug only manifests when the type comes from a CtTypeReference whose getJavaType() returns null
  ```