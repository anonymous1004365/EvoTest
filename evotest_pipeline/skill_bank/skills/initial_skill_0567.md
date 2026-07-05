---
name: executable-reference-type-mismatch
description: When handling executable reference expressions from implicit type declarations,
  test that both the declaring type and actual type parameters are correctly extracted.
  Without this skill, the TG may miss testing scenarios where method references use
  types that differ from the declaring class's type parameters.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- NULL_CHECK
- TYPE_CONVERSION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# executable-reference-type-mismatch

## Instructions

# Executable Reference Type Mismatch in Method References

## Instructions

WHEN the TG encounters code that processes method reference expressions (e.g., `ExecutableReference` or method reference AST nodes), particularly when extracting type parameters from a method reference's actual type vs its declaring type:

- THEN the TG should write a test that creates a generic class/interface (e.g., `Consumer<T>`) and a method reference to it from a context where the type argument is explicitly provided (e.g., `Consumer<String>::accept` or `Consumer<String>::andThen`).
- The test should verify that the type parameters of the **actual type** (e.g., `String` from `Consumer<String>`) are correctly reflected in the executable reference, not just the type parameters from the declaring class (e.g., `Object` or `T` from `Consumer<T>`).
- The test should confirm that the correct number and kind of type arguments are present on the method reference — on the buggy version, the test should fail because the type arguments from the declaring type shadow or replace the actual type arguments.
- Include assertions that check both the declaring type signature and the actual type reference's type parameters are present and consistent.
- Common pitfalls:
  - Testing only with non-generic method references where no type mismatch can occur.
  - Testing only with explicit lambda expressions instead of :: method references.
  - Assuming the declaring class's type parameters are sufficient without checking the actual invocation context's type arguments.
  - Not using a generic interface/class with multiple type parameters or complex generic signatures.

**Correct example (triggers the bug):**
```java
// A method reference to a generic functional interface with specific type args
// Consumer<String> cs = Consumer<String>::andThen;
// then verify that the ExecutableReference's type parameters include String, not just T/Object
```

**Incorrect example (misses the bug):**
```java
// Testing only a non-generic method reference like
// Runnable r = someObject::method;
// This bypasses type parameter extraction entirely
```