---
name: null-signature-handling-for-unbound-type-variables
description: When type signatures are computed for unbound or unresolved type parameters,
  the signature method may return null. Tests must cover this case to prevent NullPointerException
  in downstream operations like string concatenation or equals comparisons.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# null-signature-handling-for-unbound-type-variables

## Instructions

# Handling Null Signatures from Unbound Type Variables

## Instructions

- WHEN the TG encounters a method that computes or returns a "signature" for a type, type reference, or type parameter (e.g., `getSignature()`, `getQualifiedName()`, `toString()` on a type representation)
- THEN the TG should specifically test with **unbound**, **unresolved**, or **wildcard** type variables — types whose actual type argument is not yet fully resolved or is a free variable
- The TG MUST verify that when such an unbound type variable is used (e.g., its signature is called or concatenated into a parent signature), the code does **not** throw a `NullPointerException`
- Specifically, create a test scenario where:
  1. A type parameter is left as an unbound wildcard (e.g., `?` in Java generics) or an unresolved `CtTypeReference`
  2. The signature-building method is invoked on a type that contains this unbound variable
  3. The test expects this invocation to return safely (either returning a non-null default string or gracefully handling the null) instead of crashing with `NullPointerException`
- Common pitfalls to avoid:
  - **Testing only fully-resolved/bound type parameters**: A signature method may work fine for concrete types like `String` or `Integer` but fail silently when encountering a `null` from an unbound variable's signature call
  - **Assuming getSignature() always returns non-null**: The TG must not assume that intermediate signature calls always yield a valid string — `toString()` or `getSignature()` on a type variable that has no bound type may return `null`
  - **Missing the null intermediate result**: The bug is often in a chain like `parentSignature = prefix + child.getSignature() + suffix` where `child.getSignature()` returns `null`, causing `null + suffix` to produce `"nullsuffix"` silently, or worse, a `NullPointerException` if the method calls `.equals()` on the result
- At least one correct test approach: Create a type with a truly unbound type parameter (e.g., a generic type `Foo<?>` where the wildcard has no upper or lower bound), compute its full signature, and assert that the result does not throw `NullPointerException` — verifying graceful handling of the null intermediate value
- At least one incorrect test approach: Only testing `Foo<String>` or `Foo<Integer>` where all type arguments are concrete — this would miss the null-signature path entirely