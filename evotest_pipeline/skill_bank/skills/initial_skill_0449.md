---
name: property-substitution-initialization-order
description: WHEN the TG encounters code that sets or resolves property substitution
  variables (e.g., ${hostName}) that are used in configuration BEFORE they are fully
  initialized, THEN the TG should write a test that verifies property values are correctly
  set and resolved after configuration completes, catching timing-dependent lookup
  resolution bugs.
code_tags:
- PROPERTY_SUBSTITUTION
- INITIALIZATION_ORDER
test_pattern: STATE_TEST
---

# property-substitution-initialization-order

## Instructions

# Property Substitution Initialization Order

## Instructions

WHEN the TG encounters a property map or lookup mechanism (e.g., `Map<String, String>`, `StrSubstitutor`, property lookup/resolution) where:
- A dynamic property (e.g., `hostName`, `contextName`) is put into a property map AFTER configuration parsing/startup
- A configuration file (XML, properties, JSON) references this property using a substitution variable like `${hostName}`
- The property is set conditionally with `putIfAbsent` or similar conditional put

THEN the TG should:
1. Write a test that creates a `LoggerContext` (or relevant context class), triggers configuration/reconfiguration, and then checks that the property value is correctly populated in the configuration's property map
2. Verify that the expected key exists in the configuration's properties (`config.getProperties()` or similar) after the context is fully started
3. If possible, check that components (like appenders) using the property in their configuration (e.g., fileName with `${hostName}`) have the property correctly resolved in the final output
4. Test with a concrete expected value comparison — not just a null/not-null check

Mistakes to avoid:
- ONLY testing that the property was set (e.g., checking a field in LoggerContext) without checking that it's propagated to the Configuration object's properties
- Testing the property resolution in isolation without verifying the full startup/reconfiguration lifecycle
- Assuming `putIfAbsent` is called before configuration resources are parsed — the bug is that it may be called AFTER the config has already resolved the substitution, leaving the unresolved literal (e.g., `${hostName}`) in the appender's file name
- Using mocks instead of a real configuration lifecycle — this type of bug requires end-to-end initialization order verification

Example correct test (Java with JUnit):
```java
@Test
public void testPropertyIsSetBeforeConfigurationResolution() {
    // Create context and reconfigure
    ctx.reconfigure();
    // After reconfiguration, properties should contain the resolved value
    Map<String, String> props = ctx.getConfiguration().getProperties();
    assertThat(props, hasEntry("hostName", NetUtils.getLocalHostname()));
    // Also verify appender file name doesn't contain unresolved placeholder
    Appender appender = ctx.getConfiguration().getAppender("HostFile");
    // Expect resolved value, not "${hostName}" literal
    assertThat(appender.toString(), not(containsString("${hostName}")));
}
```

Example incorrect test (too shallow / misses the bug):
```java
@Test
public void testHostNameProperty() {
    // WRONG: only checks a field, not the configuration properties
    assertEquals("expected-host", ctx.getHostName());
    // WRONG: doesn't verify that the Configuration object has the property
    // The bug survives this test because the property IS set on LoggerContext,
    // but NOT propagated to configuration properties in time for resolution
}
```