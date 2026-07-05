---
name: cast-type-annotation-preservation
description: When tests involve casting expressions with type annotations, verify
  that the target type is preserved correctly after serialization/deserialization.
  This skill applies when code manipulates cast expressions and their types.
code_tags:
- VALIDATION
- STATE_MUTATION
- ORDER_DEPENDENCY
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# cast-type-annotation-preservation

## Instructions

# Cast Type Annotation Preservation

## Instructions

- WHEN the TG encounters code that creates or manipulates `CtCast` expressions (cast expressions in Java AST manipulation, particularly in the Spoon library)
- THEN it should test that the target type of a cast expression (obtained via `getType()` or similar accessors) is correctly preserved after serialization and deserialization (e.g., `CtElement.toString()` or `CtTypeReference` reconstruction), especially when the cast type involves type annotations (like `@Ann CastType`).
- Include test cases where a cast expression has a type with annotations — verify that `e.getType()` returns the same type reference after the element is cloned, serialized, or otherwise processed, comparing the qualified name or string representation before and after the operation.
- Common pitfalls: testing only unannotated cast types, or testing only the source code output (toString) without verifying the internal type reference object remains correct.
- Example correct test (pseudocode):
  ```java
  CtCast cast = factory.createCast();
  CtTypeReference<String> typeRef = factory.Type().stringType();
  typeRef.addAnnotation(factory.createAnnotation());
  cast.setType(typeRef);
  String before = cast.getType().getQualifiedName();
  String serialized = cast.toString();
  // parse back and check
  CtCast deserialized = (CtCast) factory.Type().getFromSerialized(serialized);
  assertEquals(before, deserialized.getType().getQualifiedName());
  ```
- Incorrect test (pitfall — only tests toString output, not type reference preservation):
  ```java
  // Wrong: only checks string representation, not internal type reference
  CtCast cast = ...;
  cast.setType(someTypeWithAnnotations);
  assertEquals("(String) x", cast.toString()); // passes even if type ref is corrupted
  ```