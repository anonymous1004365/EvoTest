---
name: properties-configuration-root-logger-only
description: When constructing a configuration from properties where only root logger
  entries are present, the builder may inadvertently skip initialization of internal
  state used by appender references. Tests must use a complete properties file with
  ONLY root logger configuration and verify no NullPointerException occurs.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# properties-configuration-root-logger-only

## Instructions

# Properties Configuration Root-Logger-Only Test

## Instructions

- WHEN the TG encounters a `PropertiesConfigurationBuilder` or `PropertiesConfigurationFactory` class that constructs a configuration from a properties source (e.g., a Properties object)
- THEN the TG should test with a properties configuration that defines ONLY the root logger (e.g., `logger.console.name=Console`, `logger.console.level=info`, and an appender) but NO named loggers (no `logger.<name>.name` beyond root)—such a configuration triggers an NPE because the builder does not properly initialize internal state when there are no named loggers to iterate over
- Include concrete values: use a `Properties` object with entries like `"rootLogger.level" -> "info"`, `"rootLogger.appenderRef.stdout.ref" -> "Console"`, `"appender.console.type" -> "Console"`, `"appender.console.name" -> "Console"`, and NOTHING for `logger.X.name` entries
- Verify that `PropertiesConfigurationFactory.getConfiguration()` returns a non-null configuration without throwing `NullPointerException`
- Common pitfalls: (1) testing only with properties that include both root logger AND named loggers, which masks the bug; (2) testing the builder's individual methods instead of the full `getConfiguration()` pipeline which exercises the missing state initialization; (3) forgetting to set `"rootLogger.appenderRef.stdout.ref"` in the test properties, which triggers a different code path

### Correct example
```java
@Test
public void testPropertiesConfiguration() {
    final Properties properties = new Properties();
    properties.setProperty("rootLogger.level", "info");
    properties.setProperty("rootLogger.appenderRef.stdout.ref", "Console");
    properties.setProperty("appender.console.type", "Console");
    properties.setProperty("appender.console.name", "Console");
    // NO named loggers — only root logger
    final PropertiesConfigurationFactory factory = new PropertiesConfigurationFactory();
    final PropertiesConfiguration config = factory.getConfiguration(properties);
    assertNotNull(config);
}
```

### Incorrect example
```java
@Test
public void testPropertiesConfiguration() {
    final Properties properties = new Properties();
    properties.setProperty("rootLogger.level", "info");
    // missing: rootLogger.appenderRef... and no appender entries
    // missing: any appender configuration at all
    final PropertiesConfigurationFactory factory = new PropertiesConfigurationFactory();
    final PropertiesConfiguration config = factory.getConfiguration(properties);
    // This wouldn't trigger the real bug because the NPE comes from
    // appenderRef processing when root logger references an appender
    assertNotNull(config);
}
```