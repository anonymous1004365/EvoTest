---
name: type-parameter-visitor-with-null-type
description: When visiting type parameters in AST nodes, type references may be null
  for types in the root (default) package. The TG should test that visitors handle
  null ITypeBinding#getPackage() gracefully without throwing NullPointerException,
  particularly when collecting used types from type parameters.
code_tags:
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# type-parameter-visitor-with-null-type

## Instructions

# Type Parameter Visitor with Null Package Handling

## Instructions

- WHEN the TG encounters code that visits type parameters, type arguments, or supertypes of a type declaration, especially in a visitor/analyzer that collects "used types"
- THEN it should test with a type declared in the **root (default) package** (no package declaration). For such types, `ITypeBinding.getPackage()` returns `null`, so any code that calls methods on the result of `getPackage()` (e.g., `getPackage().getName()`) without a null check will throw a `NullPointerException`.
- WHEN testing a visitor that processes type bindings (e.g., collecting used types, visiting type parameters)
  - THEN test with a class/interface in the root package that has type parameters, type arguments, or extends/implements parameterized types
  - THEN verify that the visitor does not throw `NullPointerException` and correctly processes all type information
- Common pitfalls:
  - Testing only with types in named packages (where getPackage() returns non-null), missing the root-package edge case
  - Assuming `getPackage()` always returns non-null
  - Testing type parameters but forgetting to test with root-package types that have them
- Example correct test:
  ```java
  // Create a type in root package via CtModel
  CtClass<?> rootClass = factory.createClass("RootType");
  CtTypeParameter tparam = rootClass.addFormalTypeParameter(factory.createTypeParameter("T"));
  // Trigger the visitor/code path that analyzes this type
  rootClass.accept(new CtInheritanceScanner() { ... });
  // No NullPointerException expected
  ```
- Example incorrect test:
  ```java
  // Only testing with types in a named package
  CtClass<?> pkgClass = factory.createClass("com.example.MyType");
  // This misses the null-package edge case
  ```
- The test should catch a `NullPointerException` on the buggy version when processing a type with no package.