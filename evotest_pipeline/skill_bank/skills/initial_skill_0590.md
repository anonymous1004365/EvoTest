---
name: ctnewclass-in-noclasspath-argument-types
description: ''
code_tags:
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# ctnewclass-in-noclasspath-argument-types

## Instructions

# Testing CtNewClass Argument Types in No-Classpath Mode

## Instructions

- WHEN the TG encounters a test method that creates a `CtNewClass` instance (from the Spoon framework) inside a no-classpath environment (`Launcher` with `addInputResource` and `buildModel()`),
- THEN it should verify that **both the `String` class name and the `CtTypeReference` type arguments** are properly stored in the resulting `CtNewClass` element.

- More specifically:
  - WHEN constructing a `CtNewClass` (e.g., `factory.createNewClass()`) and setting argument types via `setActualTypeArguments()`,
  - THEN the test should **access both** the `CtTypeReference`-based type arguments (via `getActualTypeArguments()`) and the `String`-based class names (via `getActualClassReferences()` or similar methods) to assert they match.

- Common pitfalls to avoid:
  1. Testing only `String`-based type arguments (e.g., `getSimpleName()`) without checking that the `CtTypeReference` equivalents are also populated correctly.
  2. Testing only `CtTypeReference`-based type arguments without checking the `String` representations.
  3. Assuming that setting one form of argument automatically ensures the other form is set — both must be explicitly verified.
  4. Using only `assertEquals` on one form and ignoring the other.

### Correct Example
```java
// Verify both String and CtTypeReference type arguments are present and match
CtTypeReference<?>[] typeRefs = ctNewClass.getActualTypeArguments().toArray(new CtTypeReference[0]);
String[] typeNames = ctNewClass.getActualClassReferences(); // or equivalent String-based getter

assertEquals("Expected number of type arguments", 2, typeRefs.length);
assertEquals("String type reference", "String", typeRefs[0].getSimpleName());
assertEquals("String class name", "java.lang.String", typeNames[0]);
assertEquals("Integer type reference", "Integer", typeRefs[1].getSimpleName());
```

### Incorrect Example (Pitfall)
```java
// Only checking CtTypeReference, missing String-based verification
CtTypeReference<?>[] typeRefs = ctNewClass.getActualTypeArguments().toArray(new CtTypeReference[0]);
assertEquals("String", typeRefs[0].getSimpleName());
// Missing: verify getActualClassReferences() also contains the right values
```