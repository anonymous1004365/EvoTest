---
name: lambda-default-constructor-generation
description: When generating default constructors for lambda bodies or anonymous classes
  in Java, the generator must produce compilable code. This skill teaches how to test
  that a default constructor correctly handles implicit vs explicit super() calls
  — particularly the distinction between an empty constructor body and no constructor
  body at all.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- CONSTRUCTOR_BODY_EMPTINESS
- DEFAULT_CONSTRUCTOR_GENERATION
test_pattern: STATE_TEST
---

# lambda-default-constructor-generation

## Instructions

# Lambda Default Constructor Generation

## Instructions

WHEN the TG encounters code that generates default constructors for lambda bodies, anonymous classes, or any implicitly-generated Java code (look for `CtConstructor` creation or `CtType.addConstructor()` patterns, especially when the generated constructor body is empty `{}`):

- THEN the TG should write a test that:
  1. Creates an input that triggers default constructor generation (e.g., a lambda expression, an anonymous class, or a class that implicitly gets a default constructor)
  2. Asserts that the generated source code compiles correctly (e.g., use `launcher.prettyprint()` and then compile the output via `javax.tools.JavaCompiler`)
  3. **Crucially**, checks whether the generated constructor body produces legal Java — specifically, an empty constructor body (`{}`) without an explicit `super()` call is illegal in some contexts, while the absence of any constructor body is not the same as an empty body.
  4. Expects that if the generator sets an empty body (`setBody(...)`) on a constructor that should have no explicit body, the output will fail to compile with an error like "call to super must be first statement in constructor body".

- Common pitfalls to avoid:
  - Testing only that the output "looks right" via prettyprint, without actually compiling it. The bug manifests only at compilation time.
  - Assuming an empty constructor body (`{}`) is always correct — Java requires an implicit `super()` call, but setting an empty body without any statement is different from having no explicit constructor body at all.
  - Testing only with simple classes and not with lambdas or anonymous classes, which trigger a different code path for constructor generation.

- Correct test example:
  ```java
  // Given a lambda in source code that Spoon processes
  Launcher launcher = new Launcher();
  launcher.addInputResource("./src/test/resources/Lambda.java");
  CtModel model = launcher.buildModel();
  CtClass<?> cls = model.getAllTypes().stream()
      .filter(t -> t.getSimpleName().equals("SomeLambdaClass"))
      .findFirst().get();
  String output = launcher.prettyprint();
  // Compile the output and assert success
  assertTrue(compileString(output), "Generated code must compile");
  ```

- Wrong test example:
  ```java
  // Only checking that the output is non-null — misses the compilation failure
  Launcher launcher = new Launcher();
  launcher.addInputResource("./src/test/resources/Lambda.java");
  CtModel model = launcher.buildModel();
  String output = launcher.prettyprint();
  assertNotNull(output); // This passes even with the bug!
  ```