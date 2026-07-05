---
name: rolling-file-properties-configuration-validation
description: When testing properties-based RollingFile configuration loading, a NullPointerException
  can occur if required configuration properties (like appender type) are missing
  or null. This skill teaches how to write tests that catch such NPEs during properties-to-configuration
  parsing.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# rolling-file-properties-configuration-validation

## Instructions

# Rolling File Properties Configuration Validation

## Instructions

- WHEN the TG encounters a configuration loading method that reads properties (e.g., `Properties`) and converts them into configuration objects (components, appenders, etc.) using a builder pattern — especially properties with prefixes like `appender.`.type, `appender.`.name
- THEN the TG should test the behavior when a required configuration property (such as the `type` field of an appender definition) is missing or null, to verify that the code handles it gracefully without throwing an uncaught `NullPointerException`
- In such a test, the TG should construct a `Properties` object that includes some but not all of the required properties for a rolling file appender (e.g., include `"appender.0.type"` set to a valid type, but omit the `"appender.0.name"` property), pass those properties to the configuration factory or builder, and verify that either:
  1. The method completes without throwing an NPE and returns an appropriate configuration object, OR
  2. It throws a meaningful exception (not NullPointerException) indicating which property was missing
- The TG should avoid: testing only with complete, well-formed property sets; assuming all properties are always present; or testing only with single-key property sets that omit the appender block entirely
- Common pitfalls: testing only with fully populated properties, not testing with partial/malformed property sets, or assuming the builder will panic early rather than dereferencing a null value

### Correct Example
```java
@Test
public void testMissingAppenderNameDoesNotCauseNPE() {
    Properties props = new Properties();
    props.setProperty("appender.0.type", "RollingFile");
    props.setProperty("appender.0.filePattern", "logs/app-%d{MM-dd-yyyy}.log.gz");
    props.setProperty("appender.0.layout.type", "PatternLayout");
    // NOTE: appender.0.name is intentionally absent
    PropertiesConfigurationBuilder builder = new PropertiesConfigurationBuilder();
    builder.setConfigurationProperties(props);
    assertDoesNotThrow(() -> builder.build());
}
```

### Incorrect Example (without this skill)
```java
@Test
public void testValidConfiguration() {
    Properties props = new Properties();
    props.setProperty("appender.0.type", "RollingFile");
    props.setProperty("appender.0.name", "RollingFile");
    // Only testing the happy path — won't catch NPE from missing name
    PropertiesConfigurationBuilder builder = new PropertiesConfigurationBuilder();
    builder.setConfigurationProperties(props);
    assertNotNull(builder.build());
}
```