---
name: template-parameter-type-validation
description: When adding named template parameters with a String name and Object value, the implementation may only accept String-typed values. This skill teaches how to test that both String and non-String (e.g., CtTypeReference) parameter values are handled correctly.
code_tags: ['NULL_CHECK', 'STATE_MUTATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that accepts template parameters with signature `addParameter(String name, Object value)` — especially in a templating/rendering context — and the implementation internally processes the parameter based on its runtime type.
- THEN the TG should write a PARAMETRIC_TEST that passes both:
  1. A `String`-typed value (e.g., `"someString"`)
  2. A non-String typed value (e.g., a custom object like a proxy class, a `CtTypeReference`, or any other Object subtype)
  
  The test MUST verify that both types of parameters are stored and retrievable without error. On the buggy version, the non-String parameter might be silently skipped, lost, or cause a NullPointerException/ClassCastException when the parameter is later used for substitution.

- Common pitfalls to avoid:
  - ❌ Testing ONLY with String-typed values, which passes on the buggy version because the bug only manifests with non-String types.
  - ❌ Testing that adding a non-String parameter throws an exception — the bug is that it is silently dropped, not that it fails loudly.
  - ❌ Only checking the parameter count without verifying the actual value stored for the non-String parameter.
  - ❌ Assuming that because `Object value` is the parameter type, all Object subtypes are handled uniformly.

- Example of a correct test (pseudocode):
  ```java
  @Test
  public void testNonStringParameterIsStored() {
      Template t = new Template("test");
      t.addParameter("myParam", 42); // non-String type
      Object retrieved = t.getParameter("myParam");
      assertEquals("Non-String parameter should be stored", 42, retrieved);
  }
  ```

- Example of an incorrect test (too narrow):
  ```java
  @Test
  public void testStringParameterIsStored() {
      Template t = new Template("test");
      t.addParameter("myParam", "hello"); // only String type
      Object retrieved = t.getParameter("myParam");
      assertEquals("hello", retrieved);
  }
  // This test would pass on the buggy version, missing the bug!
  ```