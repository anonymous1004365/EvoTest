---
name: template-proxy-type-parameter-validation
description: When validating proxy template parameters that can be either String or CtTypeReference types, tests must verify behavior with both type variants. This skill prevents incomplete type coverage when testing typed parameter handling.
code_tags: ['ARGUMENT_VALIDATION', 'BOUNDARY_CHECK', 'EDGE_CASE_INPUT', 'TYPE_CONVERSION', 'VALIDATION', 'STATE_MUTATION']
test_pattern: PARAMETRIC_TEST
---

# template-proxy-type-parameter-validation

## Instructions

# Template Proxy Type Parameter Validation

## Instructions

- WHEN the TG encounters a method that validates, processes, or iterates over template parameters (e.g., `TemplateParameter` objects, proxy template parameters, or typed parameter lists) where parameters can have different concrete types (e.g., `String` vs. `CtTypeReference<?>`)
- THEN the TG should write a test that exercises the validation logic with BOTH types of parameters:
  1. A parameter whose value is a `String` type
  2. A parameter whose value is a `CtTypeReference<?>` (or other non-String type reference)
  - Verify that the validation correctly handles the type conversion/checking for each type
  - Expect that a buggy implementation may fail (e.g., throw `ClassCastException`) when encountering one of these types due to unchecked casts like `(String)` on a `CtTypeReference` value

- Common pitfalls to avoid:
  - Testing only with `String`-typed parameters (the happy path) — this misses the bug entirely
  - Assuming all template parameters are of the same type without checking the actual type hierarchy
  - Casting without `instanceof` checks or type-safe dispatching in the production code

### Example (correct approach):

```java
// Test with String type parameter
param.setValue("someValue");
scanner.addInput(param);
// ... assert no exception

// Test with CtTypeReference type parameter
CtTypeReference<?> ref = factory.Type().createReference("java.lang.String");
param.setValue(ref);
scanner.addInput(param); // Buggy version may throw ClassCastException here
// ... assert correct behavior
```

### Example (incorrect approach — misses the bug):

```java
// Only tests String parameters — never exercises the CtTypeReference path
param.setValue("someValue");
scanner.addInput(param);
// Bug remains hidden
```