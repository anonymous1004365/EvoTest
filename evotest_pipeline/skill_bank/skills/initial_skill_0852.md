---
name: superclass-type-resolution-in-noclasspath
description: When analyzing superclass references in no-classpath mode, the JDT compiler
  may resolve a type name to an unexpected class in the same package rather than the
  intended fully-qualified type. This skill teaches how to test that the correct superclass
  type is resolved even when a same-named class exists in the local package.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# superclass-type-resolution-in-noclasspath

## Instructions

# Superclass Type Resolution in No-Classpath Mode

## Instructions

- WHEN the TG encounters code that resolves superclass types (e.g., `getSuperclass()`, `getActualClass()`, `getBoundingType()`) using JDT's no-classpath resolution
- THEN the TG should test that the resolved type correctly refers to the expected fully-qualified type, especially when a class with the **same simple name** exists in the **same package** as the referencing class
  - Create a scenario with a helper class (e.g., `InnerClass`) whose superclass is a same-named class inside the anonymous (current) package
  - Verify that `CtTypeReference.getSuperclass()` on the test element does NOT return the class from the same package but instead the fully-qualified type
  - If resolution is wrong, the superclass `getQualifiedName()` will incorrectly point to the same-package class (e.g., `<anonymous>.InnerClass`) instead of the intended fully-qualified one
  - Expect that in buggy versions, calling `getSuperclass()` on the outer type may throw an exception or return a reference pointing to the wrong package

- Common pitfalls to avoid:
  - **Do not** test only with simple types in the same package — the bug appears when the superclass has the same simple name as a class in the anonymous package
  - **Do not** forget to check the *qualified name* of the superclass reference, not just the simple name
  - **Do not** assume that adding `getActualClass()` on the reference "fixes" the resolution — verify the underlying `getSuperclass()` behavior

- Correct example:
```java
// Create a factory that adds a class to the default package
// Then verify:
CtTypeReference<?> superclassRef = typeRef.getSuperclass();
assertNotNull("Superclass reference should not be null", superclassRef);
assertEquals("Wrong superclass qualified name", 
    "com.example.expected.SuperClass", 
    superclassRef.getQualifiedName());
```

- Incorrect example (would pass on buggy version, missing the actual issue):
```java
// WRONG: only checks simple name, not qualified package resolution
assertEquals("InnerClass", typeRef.getSuperclass().getSimpleName());
// This passes even when the package is wrong
```