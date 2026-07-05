---
name: array-template-type-initialization
description: When iterating over array initialization values in template/generic code,
  type conversion of array elements can be skipped if the target type parameter is
  already a CtTypeReference. Tests should verify that each element is wrapped in a
  parameter-typed wrapper, not just checked for reference identity.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- TYPE_CONVERSION
- COLLECTION_ITERATION
test_pattern: PARAMETRIC_TEST
---

# array-template-type-initialization

## Instructions

# Array Template Type Initialization

## Instructions

- WHEN the TG encounters code that iterates over a collection of values (e.g., `List` elements) to initialize an array template where individual elements may be of generic types like `String` or `CtTypeReference<?>`
- THEN the TG should write a test that supplies a mix of `String`-typed values and `CtTypeReference<?>`-typed values in the same initialization collection, and verify that each element in the resulting array expression preserves its correct type wrapper (e.g., `CtTypeAccess` vs literal). Specifically, the test must verify that when a value is already a `CtTypeReference`, it is NOT accidentally left unwrapped (i.e., a literal) when the target array type expects typed references.
- Include concrete assertions: e.g., verify that the first element in the resulting array expression is an instance of `CtTypeAccess` (not a `CtLiteral`) when the input was a `CtTypeReference`, and that a `String`-typed input is wrapped as `CtLiteral`.
- Common pitfalls to avoid: (1) testing only with `String`-typed values and assuming all types will work the same way; (2) forgetting to check the *type* of each resulting element (e.g., only checking string content, not the AST node type); (3) not including both `String` and `CtTypeReference` inputs in the same test.

**Example (correct):**
```java
// Test that array initialization handles both String and CtTypeReference inputs
List<Object> inputs = new ArrayList<>();
inputs.add("example");
inputs.add(Factory.Type().createReference(String.class));
CtNewArray array = factory.createNewArray();
array.setElements(inputs);  // or whatever the API is
// THEN: first element is CtLiteral (String), second is CtTypeAccess
assertTrue(array.getElements().get(0) instanceof CtLiteral);
assertTrue(array.getElements().get(1) instanceof CtTypeAccess);
```

**Example (incorrect):**
```java
// Only tests String — misses the bug!
List<String> inputs = new ArrayList<>();
inputs.add("a");
inputs.add("b");
CtNewArray array = factory.createNewArray();
array.setElements(inputs);
// Bug: if CtTypeReference values are later added, they won't be wrapped
```