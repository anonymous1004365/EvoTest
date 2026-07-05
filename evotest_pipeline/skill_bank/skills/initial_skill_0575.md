---
name: field-reference-fqn-validation
description: When constructing fully-qualified field references via getFQNofFieldReference,
  teach that declaring types may be null and must be handled. Also teach that the
  access target (targetType) may need to be used as a fallback. Apply this skill when
  processing field references with potential null declaring types.
code_tags:
- TYPE_CONVERSION
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# field-reference-fqn-validation

## Instructions

# Field Reference Fully-Qualified Name Validation

## Instructions

- WHEN the TG encounters code that constructs a fully-qualified field reference name (e.g., `getFQNofFieldReference`, `getQualifiedName`, or similar field-to-string conversion) using a `declaringType` from a field reference object
- THEN the TG should test with fields where `declaringType` is `null` or unset on the field reference, to verify the method handles this case without throwing a `NullPointerException`
- WHEN testing field references with null declaring types, the TG should verify that the method falls back to the access target's type (e.g., `targetType`) or produces a reasonable default qualified name instead of crashing
- Common pitfalls: testing only with field references that have a non-null `declaringType`; assuming `declaringType` is always present; not checking for `NullPointerException` when `declaringType` is null
- Correct example: Create a `CtFieldReference` where `setDeclaringType(null)` and `setType(...)` is called, then call `getFQNofFieldReference(reference)` — expect no exception and a valid qualified name that uses the field's type as a fallback
- Incorrect example: Only testing with field references that have a fully specified declaring type — this misses the null-case bug entirely
- The test should expect the method to return a non-null, well-formed qualified name string even when declaring type is null (e.g., `"java.lang.String.myField"` using the field's own type as the declaring part)