---
name: template-parameter-type-validation
description: When validating proxy template parameters that accept generic types, tests must verify that both String and non-String (CtTypeReference) types are properly supported. The skill teaches how to construct test cases that catch missing type handling in if-else chains.
code_tags: ['NULL_CHECK', 'VALIDATION', 'TYPE_CONVERSION', 'GENERIC_METHOD_REFERENCE']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

**WHEN** the TG encounters a method that processes proxy template parameters (e.g., parameters passed to a `@Template` annotation on a proxy interface), where the method must handle parameters of different Java types (specifically `String` vs. `CtTypeReference<?>` or `Class<?>`):

- **THEN** the TG should write a test that invokes the template resolution with parameters of **both** `String` and non-String types (e.g., `CtTypeReference` wrapping a `Class<?>`), and verify that the resolved template string is correctly substituted for both cases.
- **THEN** the TG should verify that the method correctly branches on parameter type — e.g., if the code checks `param instanceof String`, then non-String parameters must fall through to a separate branch (like converting via `.getActualClass()`) rather than being silently ignored or causing an error.
- **THEN** the TG should assert the expected template output — if the template is `"select * from t where id = #{%s}"` and a parameter is a `CtTypeReference<Integer>`, the resolved output should be `"select * from t where id = #{Integer}"` or equivalent, not `"select * from t where id = #{}"`.

**Common pitfalls to avoid:**
- Testing only `String`-typed parameters in templates, which masks the bug where non-String parameters are silently skipped
- Assuming that `toString()` on a `CtTypeReference` returns the simple class name — the TG should verify the format (e.g., `Integer.class` → `"Integer"` vs `"java.lang.Integer"`)
- Forgetting to instantiate concrete implementations of abstract types (e.g., `CtTypeReference` requires an anonymous subclass or mock)

**Correct example (catches the bug):**
```java
// Given a proxy interface method like:
// @Template("select * from t where id = #{%s}")
// void findById(Integer id);

// Test that both String and type parameters work:
CtTypeReference<Integer> intRef = new AbstractQuery.CtTypeReference<Integer>() {
    @Override
    public Class<Integer> getActualClass() {
        return Integer.class;
    }
};

String result1 = resolver.resolve("select * from t where id = #{%s}", "42");
assertEquals("select * from t where id = #{42}", result1);

String result2 = resolver.resolve("select * from t where id = #{%s}", intRef);
assertEquals("select * from t where id = #{Integer}", result2);
```

**Incorrect example (misses the bug):**
```java
// Only tests String parameters:
String result = resolver.resolve("select * from t where id = #{%s}", "42");
assertEquals("select * from t where id = #{42}", result);
// Buggy code would pass this test, but fail when a CtTypeReference is passed.
```