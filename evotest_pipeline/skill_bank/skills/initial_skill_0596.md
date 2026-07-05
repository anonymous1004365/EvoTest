---
name: template-parameter-type-validation
description: Detects bugs where a method modifies abstract syntax tree (AST) elements with template parameters of mixed types (e.g., String and CtTypeReference) without proper type validation, leading to cast exceptions downstream. Use when testing AST manipulation methods that accept or process template parameters.
code_tags: ['ARGUMENT_VALIDATION', 'STATE_MUTATION']
test_pattern: INTERACTION_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation in AST Manipulation

## Instructions

- WHEN the Test Generator (TG) encounters a method that adds, processes, or validates template parameters (e.g., parameters whose values can be either `String` or `CtTypeReference<?>`) in an abstract syntax tree (AST) model
- THEN the TG should write an interaction-style test that:
  1. Creates a method or class element in the AST (e.g., a `CtClass`, `CtInterface`, or `CtMethod`)
  2. Adds a template parameter using one type (e.g., a `String` value like `"T"`)
  3. Adds another template parameter using a different type representation (e.g., a `CtTypeReference` created from a type like `List.class`)
  4. Triggers a serialization, pretty-printing, or downstream processing call on the AST element (e.g., a `toString()`, `printElement()`, or any visit/accept method)
  5. Verifies that the operation completes without throwing a `ClassCastException` or other unexpected exceptions

- The TG should ensure the test:
  - Uses **both** `String` and `CtTypeReference` types as template parameter values (not just one type)
  - Triggers the downstream processing that would normally cast parameters (e.g., model building, printing, or transformation)
  - Does NOT assume all template parameters are homogeneous (same type) — the bug manifests when types are mixed
  - Checks that the output (e.g., string representation, serialized form) correctly represents both parameter types

- **Common pitfalls to avoid:**
  - ❌ Only testing template parameters of a single type (e.g., only `String` parameters)
  - ❌ Only testing creation of template parameters without triggering downstream processing
  - ❌ Assuming that because parameters can be added individually, they can be processed together regardless of type
  - ❌ Not catching the `ClassCastException` that occurs when code assumes all parameters are the same type

- **Example correct test pattern:**

```java
// Create the AST element
CtClass<?> cls = factory.createClass("MyClass");

// Add a template parameter as a String
cls.addTemplateParameter("T");

// Add a template parameter as a CtTypeReference
CtTypeReference<?> ref = factory.Type().createReference(List.class);
cls.addTemplateParameter(ref);

// Trigger downstream processing that exposes the bug
// Expect this NOT to throw ClassCastException
cls.toString(); // or cls.accept(printer), etc.
```

- **Example INCORRECT test pattern:**

```java
// ❌ Only adds String-type parameters, missing the mixed-type scenario
CtClass<?> cls = factory.createClass("MyClass");
cls.addTemplateParameter("T1");
cls.addTemplateParameter("T2");

// ❌ Never triggers the actual processing that would cast the parameters
// No toString(), accept(), or serialization call
```