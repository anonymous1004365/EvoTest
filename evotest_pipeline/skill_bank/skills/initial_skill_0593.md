---
name: unknown-declaration-proxy-type-resolution
description: When a test generates or processes proxy/unknown type declarations, the
  code must handle null type references gracefully instead of throwing NPE. Use this
  skill when testing methods like getJavaType() on declarations with incomplete or
  missing Java type information.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# unknown-declaration-proxy-type-resolution

## Instructions

# Unknown/Proxy Declaration Type Resolution

## Instructions

- **WHEN** the TG encounters code that resolves a `CtTypeReference` or calls `getJavaType()` on a declaration (e.g., a proxy, implicit, or unknown declaration) — such as a `spoon.reflect.declaration.CtTypedElement` that may not have a proper backing Java type (e.g., `CtAnnotation`-like or declaration elements with incomplete type info)

- **THEN** the TG should write a test that:
  1. Creates or obtains a declaration instance whose `getJavaType()` or `getType()` method may return `null` (e.g., an unknown/proxy declaration, an implicit element, or a method-typed element without a real Java type reference)
  2. Calls the method(s) that internally call `getJavaType()` or a type-resolving helper — for example, a method that converts the declaration's type to a JDT-compatible `ITypeBinding`, a method called `getJavaType()`, or any method that accesses the type reference without a null guard
  3. Expects that the method **does not throw a NullPointerException**, returning `null` or `"null"` string, or an appropriate fallback value when the type reference is null

- **Concrete example**: For a spoon-like code analysis framework, create a test that:
  - Gets an unknown declaration (e.g., from a factory or builder that produces proxy/implicit elements)
  - Gets the type of that declaration via e.g. `element.getType()` where the result may be null
  - Calls `getJavaType()` on that null type reference
  - **Verifies**: No `NullPointerException` occurs; the code handles null gracefully (e.g., returns `null` instead of calling `.getQualifiedName()` on null)

- **Common mistakes to avoid**:
  - ❌ Testing only with well-formed declarations that have proper type references — the bug only manifests with proxy/unknown/incomplete declarations
  - ❌ Assuming `getType()` always returns a non-null `CtTypeReference` — it may return `null` for implicit elements, unknowns, or annotations
  - ❌ Only testing the "happy path" where all calls succeed — the fix adds null checks at call sites like `type.getJavaType()` where `type` could be null
  - ❌ Testing in isolation without triggering the actual code path that calls `getJavaType()` on a null type — the NPE typically occurs in a helper called during `toString()`, `getSimpleName()`, or similar string-rendering methods

- **Correct approach** — test that a null type reference is handled:
  ```java
  @Test
  public void testUnknownDeclarationHandlesNullType() {
      // Setup: get a declaration whose getType() returns null (e.g., unknown/proxy)
      CtType<?> unknownDecl = factory.Type().get("some.nonexistent.Type");
      // When the type is null, toString() / getJavaType() should not throw
      assertNull(unknownDecl.getType());  // ensure type is null
      // The method under test should handle null gracefully
      String result = unknownDecl.getQualifiedName();  // or toString()
      assertNotNull(result);  // should not throw NPE
  }
  ```

- **Incorrect approach** — testing only happy path:
  ```java
  @Test
  public void testNormalDeclaration() {
      // Bug won't be triggered because normal types always have non-null type ref
      CtType<?> normalDecl = factory.Type().get("java.lang.String");
      assertNotNull(normalDecl.getType());
      normalDecl.getQualifiedName();  // always works, never triggers the bug
  }
  ```