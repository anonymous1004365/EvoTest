---
name: import-scanner-javadoc-resolution
description: When testing an import scanner's ability to resolve types from Javadoc
  references, verify that the scanner correctly processes fully-qualified type names
  (e.g., "java.util.Map") as well as unqualified names across various Javadoc contexts
  like @see, @link, and @throws.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# import-scanner-javadoc-resolution

## Instructions

## Guidance

# Import Scanner Javadoc Type Resolution

## Instructions

- WHEN the TG encounters an `ImportScanner` or similar type-resolution implementation that processes Javadoc comments to discover required imports
- THEN the TG should write parameterized tests that verify the scanner correctly resolves type references from all standard Javadoc tags (`@see`, `@link`, `@linkplain`, `@throws`, `@param`)
- The test MUST include test cases where the Javadoc reference uses a fully-qualified type name (e.g., `{@link java.util.Map}` or `@see java.util.Map`) and verify that the import scanner reports that type (e.g., `java.util.Map`) in its discovered imports
- The test MUST also include test cases with types that do NOT exist (e.g., `@see com.example.NonExistentClass`) to verify the scanner handles missing types gracefully
- Common pitfalls: testing only with simple type names rather than fully-qualified ones; testing only `@see` tags while ignoring `@link` in inline Javadoc; forgetting to test that the scanner returns the canonical name (e.g., `java.util.Map` not `Map`)
- Correct example: `@Test void testImportByJavaDoc() { ... assertThat(scanner.getImports()).contains("java.util.Map"); }`
- Incorrect example: testing only that `@see Map` resolves to `Map` without the package prefix, or only testing `@see` while ignoring `{@link java.util.Map}`