---
name: template-parameter-type-validation
description: This skill teaches TG to write tests that verify template parameter type validation in parsers, specifically when iterating over a product type hierarchy where only certain parameter types (e.g., String) are recognized while others (e.g., CtTypeReference) are silently ignored, causing different interpretation of the same construct.
code_tags: ['NULL_CHECK', 'BOUNDARY_CHECK', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that iterates over parameters/elements of a parsed construct (such as an async/await expression), visiting or populating properties based on parameter types:
  - THEN the TG should write a test that calls the parser with BOTH a `String` literal parameter AND a non-`String` typed parameter (e.g., a `CtTypeReference` expression, or any property reference) for the same construct.
  - The test should verify that parsing succeeds and yields the expected AST structure (e.g., the correct number of children/parameters in the parsed output), confirming that the parser correctly handles the full type hierarchy, not just String parameters.
  - Specifically, for an async function with an await expression inside, test with: (a) `await x;` where `x` is a simple identifier, and (b) `await x;` where `x` appears earlier as a parameter that could be resolved to a non-String type like `Promise<X>`.

- WHEN a parser iterates over a product type's variants (e.g., `String` and `CtTypeReference`), only handling one variant (e.g., `String`) and silently skipping the other:
  - THEN the TG should write a test where the non-handled variant is present, and assert that parsing does NOT result in a silently incomplete AST (e.g., an `await` expression with 0 parameters/children instead of 1).
  - The test should expect the correct number of properties/children (e.g., 1 child for `await x;`) and fail on the buggy version that drops non-String parameters.

- Common pitfalls:
  - Testing only String-type parameters, which passes on the buggy version because the bug only manifests with non-String parameter types.
  - Not checking the number of children/properties in the parsed AST, only checking that parsing doesn't throw an exception — missing the silent data loss.
  - Assuming that all parameter types are handled equally when the iteration logic has a type-specific branch.

- Correct example:
  ```java
  @Test
  public void testAwait() {
      // Parse an async function with await expression where the await operand is a
      // non-String typed parameter (e.g., from a previous binding)
      String source = "async function f() { let x = Promise.resolve(1); await x; }";
      Script script = parse(source);
      // Verify the await expression has exactly 1 child/parameter
      assertEquals(1, script.statements.get(0).body.expressions.get(0).params.size());
  }
  ```

- Incorrect example (won't catch the bug):
  ```java
  @Test
  public void testAwaitStringOnly() {
      // Only testing with a string literal — this passes even on the buggy version
      String source = "async function f() { await 'ok'; }";
      Script script = parse(source);
      assertNotNull(script);
  }
  ```