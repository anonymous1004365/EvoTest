---
name: jndi-registry-type-filtering
description: When implementing a Registry that wraps JNDI, test that lookupByType
  correctly filters by class type and returns only type-matching beans. The TG should
  verify that non-matching types are excluded from results — a common bug is returning
  beans that don't match the requested type.
code_tags:
- NULL_CHECK
- TYPE_SAFETY_VALIDATION
- ITERATION_OVER_COLLECTION
test_pattern: STATE_TEST
---

# jndi-registry-type-filtering

## Instructions

# JNDI Registry Type Filtering

## Instructions

- WHEN a `JndiRegistry` (or any `Registry` implementation that wraps a JNDI-like context) is being tested and it has a `lookupByType(Class<T> type)` or `findByTypeWithName(Class<T> type)` method that iterates over bound entries
- THEN the test MUST:
  1. Bind multiple beans of **different types** to the registry (e.g., `SimpleLanguage` which implements `Language`, and a `String` like `"Hello bar"` which does NOT implement `Language`).
  2. Call `lookupByType(Language.class)` (or the relevant supertype).
  3. Assert that the result map has exactly the expected size (e.g., `assertEquals(1, set.size())`) — only beans that are `instanceof` the requested type should be included.
  4. Assert that the correct key name is present in the result (e.g., `assertEquals("foo", key)`).
  5. Verify the returned value is the same object as the one bound (e.g., `assertSame(jndi.lookupByName("foo"), set.values().iterator().next())`).
- The test must use `JndiRegistry` constructed with `JndiTest.createInitialContext()` (or equivalent) so that it creates a minimal in-memory JNDI context.
- Common pitfalls to avoid:
  - ❌ **Binding only one type** (e.g., only `SimpleLanguage` objects) — this misses the bug where non-matching types are incorrectly included.
  - ❌ **Not calling `lookupByType` with a supertype** — must test that subtype instances are found when looking up the parent type (e.g., `SimpleLanguage` found when looking up `Language.class`).
  - ❌ **Forgetting to check the size of the result map** — the bug manifests as `expected:<1> but was:<0>` because the iteration fails to find the matching bean due to a JNDI context issue.
  - ❌ **Not verifying the key name** — ensure the bound name `"foo"` is present in the result map keys, not just the size.

### ✅ Correct test approach:
```java
JndiRegistry jndi = new JndiRegistry(JndiTest.createInitialContext());
jndi.bind("foo", new SimpleLanguage());   // matches Language type
jndi.bind("bar", "Hello bar");            // does NOT match Language type

Map<String, ?> set = jndi.lookupByType(Language.class);
assertNotNull(set);
assertEquals(1, set.size());  // Only "foo" should match
String key = set.keySet().iterator().next();
assertEquals("foo", key);
```

### ❌ Incorrect test approach (would miss the bug):
```java
JndiRegistry jndi = new JndiRegistry(JndiTest.createInitialContext());
jndi.bind("foo", new SimpleLanguage());
// Missing a non-matching binding!

Map<String, ?> set = jndi.lookupByType(Language.class);
assertNotNull(set);
assertEquals(1, set.size());  // This passes even if the buggy code returns 0 because nothing matches
```