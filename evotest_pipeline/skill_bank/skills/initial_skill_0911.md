---
name: lambda-union-catch-type-validation
description: When processing lambda expressions with union type catch (multi-catch)
  in no-classpath mode, validate that all exception types referenced in the catch
  clause are properly resolved. This skill helps write tests that detect missing or
  incomplete type resolution for union catch exception types inside lambdas.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# lambda-union-catch-type-validation

## Instructions

# Lambda Union Catch Type Validation in No-Classpath Mode

## Instructions

- WHEN the TG encounters code that processes lambda expressions containing multi-catch (union type) exception clauses (e.g., `catch (IllegalArgumentException | IllegalStateException e)`) **in no-classpath mode**, where the code attempts to resolve or validate the exception types referenced in the catch clause
- THEN the TG should write a test that:
  1. Creates a source code string containing a lambda expression with a multi-catch clause (union type) inside a method
  2. Parses the code in no-classpath mode
  3. Verifies that the model is built without exceptions (e.g., `NoClassDefFoundError` or other resolution failures)
  4. Checks that the union catch exception types are correctly represented in the resulting AST model
  5. Expects that on the buggy version, the test fails with an exception (e.g., `NullPointerException`, `NoClassDefFoundError`, `IndexOutOfBoundsException`, or `ClassNotFoundException`) due to improper resolution of one or more exception types in the union catch clause

- **Common pitfalls:**
  - Testing only single-catch (non-union) exception clauses, which do not exercise the problematic code path
  - Testing lambda expressions without exception handling, which does not trigger the union type resolution logic
  - Testing multi-catch outside of lambda expressions, which may use a different code path
  - Assuming that if one exception type in the union resolves correctly, all of them do — the bug may affect only *subsequent* exception types after the first one in the union
  - Writing tests that only parse the code but don't access the lambda/model elements, which may not trigger lazy resolution

- **Correct example:**
  ```java
  @Test
  public void testUnionCatchExceptionInsideLambdaInNoClasspath() {
      // contract: union catch exception types inside lambda in no classpath should be handled
      String source = "class A { void m() { java.util.function.Consumer<String> c = (s) -> { try { } catch (IllegalArgumentException | IllegalStateException e) { } }; } }";
      SpoonModelBuilder builder = new Launcher().createModelBuilder();
      builder.addInputSource(new FileSource(...));
      builder.setSourceClasspath(new String[0]); // no-classpath mode
      builder.build();
      // If this point is reached without exception, the test PASSES
      // On the buggy version, this should throw an exception
  }
  ```

- **Incorrect example (does NOT exercise the bug):**
  ```java
  @Test
  public void testLambdaWithoutCatch() {
      // Only tests basic lambda, no union catch — won't trigger the bug
      String source = "class A { void m() { java.util.function.Consumer<String> c = (s) -> System.out.println(s); } }";
      // ... parsing and assertions that always pass
  }
  ```