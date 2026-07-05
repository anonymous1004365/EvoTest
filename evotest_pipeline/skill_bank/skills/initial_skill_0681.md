---
name: bean-name-cache-key-mismatch
description: WHEN a method caches computed bean names using a key different from the
  lookup key, the cache may always miss. THEN the test must exercise a second field
  with the same base type but a different generic type to expose the key mismatch.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- CONCURRENCY
- CACHE_OPERATIONS
test_pattern: STATE_TEST
---

# bean-name-cache-key-mismatch

## Instructions

# Bean Name Cache Key Mismatch

## Instructions

WHEN the code under test contains a `ConcurrentMap`-backed cache (e.g. `ConcurrentMap<SimpleEntry<Class<?>, Class<?>>, String> beanNameCache`) where:

- **Lookup** uses `beanNameCache.get(fieldType)` — looking up by only the raw `Class<?>` (the field's declared type), missing the generic component.
- **Insert** uses `beanNameCache.putIfAbsent(keyPair, name)` where `keyPair` is a `SimpleEntry<Class<?>, Class<?>>` (field type + generic type).

THEN the TG should write a test that:

1. Declares **two fields** in a test injectable class that share the **same raw field type** (e.g. `List<String>` and `List<Integer>` both have field type `List.class`) but have **different generic type parameters**.
2. Calls `getFieldValue(field, obj)` on the **first field** to populate the cache.
3. Calls `getFieldValue(field, obj)` on the **second field** — on the buggy version, the cache lookup with `fieldType` (same for both) returns the cached value from step 2 immediately, so **no fresh lookup occurs**, and the **wrong bean name** is returned for the second field.
4. Verifies that the returned object for each field is the **correct bean** (e.g. by checking `getBeanName()` on the `SpringBeanLocator` attached to the proxy, or by casting and calling a method specific to the generic type).

**Common pitfalls to avoid:**
- Testing only a **single field** per type — the bug only manifests when a second field with the same raw type but different generic type is resolved *after* the first.
- Assuming that `SimpleEntry`-based cache key (`fieldType, generic`) and the lookup key (`fieldType` alone) match — they do not, which is the root cause.
- Forgetting that the test must actually **invoke the field resolution twice** in sequence (first one populates with key1, second one looks up with wrong key2 and incorrectly hits).
- Using `@SpringBean` annotations where `name` is explicitly set — that bypasses the `getBeanName()` method entirely because `Strings.isEmpty(name)` is `false`.

**Example (correct):**

```java
// Test injectable class
static class InjectableWithGenericBeans
{
    @SpringBean
    private Bean<String> stringBean;  // field type = Bean.class, generic = String.class

    @SpringBean
    private Bean<Integer> intBean;    // field type = Bean.class, generic = Integer.class
}

// In test:
Field field1 = obj.getClass().getDeclaredField("stringBean");
Object proxy1 = factory.getFieldValue(field1, obj);

Field field2 = obj.getClass().getDeclaredField("intBean");
Object proxy2 = factory.getFieldValue(field2, obj);

// On buggy version: proxy2 reuses the cached bean name from stringBean
// On fixed version: proxy2 gets the correct bean name for Bean<Integer>
SpringBeanLocator locator1 = (SpringBeanLocator)((ILazyInitProxy)proxy1).getObjectLocator();
SpringBeanLocator locator2 = (SpringBeanLocator)((ILazyInitProxy)proxy2).getObjectLocator();

assertEquals("stringBeanBeanName", locator1.getBeanName());  // passes both
assertEquals("intBeanBeanName", locator2.getBeanName());      // passes fixed, fails buggy
```

**Example (incorrect — misses the bug):**

```java
// ❌ Only one field tested per type — cache bug never triggered
Field field = obj.getClass().getDeclaredField("stringBean");
Object proxy = factory.getFieldValue(field, obj);
SpringBeanLocator locator = (SpringBeanLocator)((ILazyInitProxy)proxy).getObjectLocator();
assertEquals("stringBean", locator.getBeanName());
// Only one resolution — cache never returns stale result
```