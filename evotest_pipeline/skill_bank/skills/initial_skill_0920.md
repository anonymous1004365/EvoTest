---
name: snippet-context-type-filtering
description: When compiling code snippets against a given context, the type resolver
  must correctly filter out non-CtTypeReference parameters (like String) when matching
  proxy template parameters to actual types. This skill teaches how to test that type
  proxy resolution only considers CtTypeReference typed parameters and ignores others
  to avoid ClassCastException.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# snippet-context-type-filtering

## Instructions

# Snippet Context Type Proxy Resolution

## Instructions

- WHEN the TG encounters a method that resolves types by iterating over parameters of a proxy template (e.g., `getActualClass()` or similar type resolution in a snippet compilation context), and those parameters could be of types other than `CtTypeReference` (e.g., `String` parameter names),
- THEN the TG should write a test that:
  1. Creates a snippet that uses the type whose proxy template has non-CtTypeReference parameters (e.g., a type with a `String` parameter)
  2. Calls the snippet compilation method (e.g., `compileSnippet`) with a context that provides actual values for those parameters
  3. Asserts that the snippet compiles successfully without throwing a `ClassCastException`
- Specifically, the test should verify that when iterating over template parameters, the code checks `if (parameter instanceof CtTypeReference)` before attempting to cast or use it as a type parameter. Without this check, a `ClassCastException` occurs when trying to cast a non-CtTypeReference (e.g., a `String` parameter name) to `CtTypeReference` in type resolution logic.
- Common pitfalls to avoid:
  - ❌ Testing only with proxy templates where ALL parameters are `CtTypeReference` types (this will not trigger the bug)
  - ❌ Assuming that all template parameters are always type references — they may be parameter names (Strings) as well
  - ❌ Not providing a full context that includes actual values for all template parameters (the compile must complete fully)

### Example

**Correct test** (catches the bug):
```java
// Given a generic type like: class Gen<T> { T t; }
// And a snippet referencing Gen<String> via a proxy template with a mix of parameter types
// Force the type resolution to encounter a non-CtTypeReference parameter
Factory factory = createFactory();
CtType<?> type = factory.Type().get("some.package.Gen");
// ... setup proxy template with mixed parameter types ...
Snippet snippet = new Snippet();
snippet.setCompilationUnit(...);
// This should NOT throw ClassCastException
snippet.compile();
```

**Incorrect test** (misses the bug):
```java
// Only tests where all proxy template parameters are CtTypeReference instances
// This won't trigger the type filtering bug
Snippet snippet = new Snippet();
// ... setup with only CtTypeReference parameters ...
snippet.compile(); // passes even with buggy code
```