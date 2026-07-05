---
name: converter-registry-replace-checks-identity
description: WHEN testing a converter registry that caches converters by class name,
  THEN use assertSame to verify the registry returns the exact same converter instance
  that was registered. This catches bugs where set() creates a new converter instead
  of storing the instance passed in.
code_tags:
- NULL_CHECK
- VALIDATION
- ACCESS_CONTROL_EVALUATION
test_pattern: STATE_TEST
---

# converter-registry-replace-checks-identity

## Instructions

# Converter Registry Must Return the Same Instance That Was Set

## Instructions

- WHEN the TG encounters a converter locator/registry class (like `ConverterLocator`) that has:
  - A `set(Class<?>, IConverter<?>)` method to register converters by type
  - A `getConverter(Class<?>)` or `get(Class<?>)` method to retrieve converters by type
  - An internal cache (e.g., `Map<String, IConverter<?>>`) keyed by class name

- THEN the TG should write a test that:
  1. Creates an instance of the registry (e.g., `ConverterLocator locator = new ConverterLocator()`)
  2. Obtains a converter instance for a specific type (e.g., `Date.class`) by calling `locator.getConverter(Date.class)`
  3. Obtains the converter again for the same type by calling `locator.getConverter(Date.class)` a second time
  4. Uses `assertSame()` (NOT `assertEquals()`) to verify that both calls return the **exact same Java object reference**
  - Expected behavior on the buggy version: `assertSame` fails because the registry returns a different instance each time `getConverter` is called for certain types
  - Expected behavior on the fixed version: `assertSame` passes because the registry caches and returns the same instance

- Common pitfalls to avoid:
  - Using `assertEquals()` instead of `assertSame()` — this only checks value equality, not reference identity, and may not catch the bug
  - Testing only with String or primitive types (e.g., `Integer.class`, `Boolean.class`) — these may use singletons that happen to pass; date-related types like `Date.class` are more likely to exhibit the bug
  - Testing `get()` (the package-private lookup method) instead of `getConverter()` (the public API method) — the bug may only be in the public API path
  - Assuming that because a converter is registered in the constructor, it must be cached as the same instance — the constructor might call `set()` with `new DateConverter()` each time, but the `getConverter()` method might create a new one on each invocation instead of returning the cached one

### Correct example (testing Date converter identity):
```java
ConverterLocator locator = new ConverterLocator();
IConverter<Date> converter1 = locator.getConverter(Date.class);
IConverter<Date> converter2 = locator.getConverter(Date.class);
assertSame("getConverter must return the same instance for Date.class on subsequent calls",
    converter1, converter2);
```

### Incorrect example (using assertEquals, which may pass even if references differ):
```java
ConverterLocator locator = new ConverterLocator();
IConverter<Date> converter1 = locator.getConverter(Date.class);
IConverter<Date> converter2 = locator.getConverter(Date.class);
assertEquals(converter1, converter2); // This may pass even if they are different objects!
```