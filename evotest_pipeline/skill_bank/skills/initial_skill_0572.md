---
name: catch-variable-type-resolve
description: When a CtCatchVariable (or similar catch variable) is declared with a
  union type (multi-catch), its getType() method may return null. Tests must verify
  that getType() returns a non-null CtTypeReference for each exception type in the
  multi-catch, including non-generic and generic exception types.
code_tags:
- TYPE_CONVERSION
- NULL_CHECK
test_pattern: STATE_TEST
---

# catch-variable-type-resolve

## Instructions

# Catch Variable Type Resolution in Multi-Catch

## Instructions

- WHEN the TG encounters code that uses `CtCatchVariable` (a catch variable in a try-catch block), particularly with multi-catch syntax (e.g., `catch (IOException | RuntimeException e)`)
- THEN the TG should write a test that:
  1. Creates a try-catch block with a multi-catch clause (e.g., `catch (IOException | RuntimeException e)`)
  2. Retrieves the `CtCatchVariable` from the catch clause
  3. Calls `getType()` on the catch variable
  4. Verifies that `getType()` returns **a non-null `CtTypeReference`** for **each** exception type in the multi-catch (e.g., call `getType()` and assert it is not null)
  5. Optionally, verify the returned type reference's qualified name matches the expected exception class (e.g., `"java.io.IOException"` or `"java.lang.RuntimeException"`)
- Common pitfalls to avoid:
  - Testing only with a single exception type in the catch clause (single-catch) — the bug specifically manifests with multi-catch (union types)
  - Testing only String-based type parameters or non-generic exception types — the bug can also occur with generic parameterized types in catch variables
  - Assuming `getType()` always returns a non-null value for catch variables — the buggy version may return null for multi-catch variables because the type information is not properly resolved
  - Writing only one assertion and missing the fact that each exception type in the multi-catch must be tested

### Example (Correct)

```java
// Given a method that contains a try-catch with multi-catch:
// try { ... } catch (IOException | RuntimeException e) { ... }

CtCatch ctCatch = ...; // retrieve the CtCatch element
CtCatchVariable<?> catchVar = ctCatch.getParameter();
CtTypeReference<?> typeRef = catchVar.getType();
assertNotNull("getType() should not return null for multi-catch variable", typeRef);
```

### Example (Incorrect — would not catch the bug)

```java
// Single catch only — does not trigger the multi-catch bug
CtCatch ctCatch = ...; // single-catch: catch (IOException e)
CtCatchVariable<?> catchVar = ctCatch.getParameter();
CtTypeReference<?> typeRef = catchVar.getType();
assertNotNull(typeRef); // passes even in buggy version because single-catch works
```