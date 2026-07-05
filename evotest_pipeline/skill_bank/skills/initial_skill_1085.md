---
name: classloader-resource-nullpointer
description: ''
code_tags:
- NULL_CHECK
- CLASSLOADER_RESOURCE_LOADING
test_pattern: EXCEPTION_TEST
---

# classloader-resource-nullpointer

## Instructions

# Testing Classloader Resource Prefix Does Not Cause NullPointerException

## Instructions

- WHEN the test exercises `Configurator.initialize(name, configLocation)` with a configLocation string that contains the prefix `"classloader:"` (e.g., `"classloader:log4j2-config.xml"`)
- THEN the test must verify that no `NullPointerException` is thrown during initialization.
  Use `assertDoesNotThrow(() -> Configurator.initialize("Test1", "classloader:log4j2-config.xml"))` as the assertion.
- The same precaution applies to any prefix-based resource location where the underlying resource resolution could return null
  (e.g., `"classpath:..."`, custom prefixes). Test each prefix variant independently.
- Common pitfall: Testing only the `"classpath:"` prefix and assuming `"classloader:"` behaves identically.
  The two prefixes resolve via different code paths and may have different null-safety properties.
  Always test each prefix explicitly.

### Correct Example

```java
@Test
public void testFromClassPathWithClassLoaderPrefix() throws Exception {
    assertDoesNotThrow(() -> {
        try (final LoggerContext ctx = Configurator.initialize("Test1", "classloader:log4j2-config.xml")) {
            assertNotNull(ctx);
        }
    });
}
```

### Incorrect Example (missing the "classloader:" case)

```java
@Test
public void testFromClassPathOnly() throws Exception {
    // Only tests "classpath:" prefix, missing the "classloader:" prefix entirely
    try (final LoggerContext ctx = Configurator.initialize("Test1", "classpath:log4j2-config.xml")) {
        assertNotNull(ctx);
    }
}
```