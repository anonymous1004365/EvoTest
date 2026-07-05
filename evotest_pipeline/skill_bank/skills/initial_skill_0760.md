---
name: jndi-lookup-nonstring-type-safety
description: When testing JNDI lookups that return non-String objects, ensure the
  lookup method converts Object to String using Objects.toString()/String.valueOf()
  instead of relying on implicit toString() which can cause ClassCastException. Use
  this skill when testing StrLookup implementations that wrap JNDI Manager lookups
  returning Object.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# jndi-lookup-nonstring-type-safety

## Instructions

# JNDI Lookup Non-String Type Safety

## Instructions

- WHEN the test encounters a `StrLookup` implementation (like `JndiLookup`) whose `lookup()` method calls `jndiManager.lookup()` which returns `Object` (via generic `<T> T lookup(String name)`), and the lookup method's return type is `String`
- THEN the test should verify that the lookup correctly handles non-String bound values (e.g., `Integer`, `Collection<String>`) without throwing a `ClassCastException`. Specifically:
  - Bind an `int`/`Integer` value (e.g., `42`) under a JNDI name and call `lookup(name)` on the `StrLookup` instance
  - Assert that the result equals `String.valueOf(42)` (i.e., `"42"`)
  - Bind a `Collection` value (e.g., `Arrays.asList("one", "two", "three")`) under a JNDI name and call `lookup(name)`
  - Assert that the result equals `String.valueOf(collection)` (i.e., `"[one, two, three]"`)
- WHEN using JNDI in tests, use `@Rule public JndiRule jndiRule = new JndiRule(createBindings())` to set up the JNDI environment, where `createBindings()` returns a `Map<String, Object>` with keys prefixed by `JndiLookup.CONTAINER_JNDI_RESOURCE_PATH_PREFIX` (i.e., `"java:comp/env/"`)
- THEN the test should verify that no `ClassCastException` occurs when non-String objects are retrieved through the lookup chain (JndiManager.lookup → JndiLookup.lookup)
- Common pitfalls to avoid:
  - Testing only `String` type bound values — this masks the bug because only `String` instances can be safely cast to `String`
  - Assuming `Object.toString()` is implicitly called — the bug occurs because `Objects.toString(value, null)` expects an `Object` and calls `toString()` on it, but if the value was already wrongly cast to `String` somewhere in the chain, a `ClassCastException` is thrown before `toString()` is reached
  - Forgetting to register non-String bindings in the JNDI test rule's binding map

### Correct Example
```java
@Rule
public JndiRule jndiRule = new JndiRule(createBindings());

private Map<String, Object> createBindings() {
    final Map<String, Object> map = new HashMap<>();
    map.put(JndiLookup.CONTAINER_JNDI_RESOURCE_PATH_PREFIX + "int-value", 42);
    map.put(JndiLookup.CONTAINER_JNDI_RESOURCE_PATH_PREFIX + "string-collection",
            Arrays.asList("one", "two", "three"));
    return map;
}

@Test
public void testNonStringLookup() {
    final StrLookup lookup = new JndiLookup();
    final String integralValue = lookup.lookup("int-value");
    assertEquals("42", integralValue);  // No ClassCastException expected
    
    final String collectionValue = lookup.lookup("string-collection");
    assertEquals("[one, two, three]", collectionValue);  // No ClassCastException expected
}
```

### Incorrect Example (masks the bug)
```java
// BAD: Only tests String-typed JNDI values
@Test
public void testLookup() {
    final StrLookup lookup = new JndiLookup();
    assertEquals("app-1", lookup.lookup("logging/context-name"));  // Only String values tested
    assertNull(lookup.lookup("logging/non-existing-resource"));
    // MISSING: Testing lookup with Integer, Collection, or other non-String objects
}
```