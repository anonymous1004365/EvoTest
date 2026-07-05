---
name: system-property-override-test-isolation
description: When a test modifies system properties that affect configuration loading
  (like log4j.configurationFile), the test must explicitly set the property before
  calling the configuration method and verify the correct config is loaded, not a
  default. Use this skill when testing code that reads system properties to determine
  configuration behavior.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# system-property-override-test-isolation

## Instructions

# System Property Override Test Isolation

## Instructions

- WHEN the TG encounters code that reads a system property to determine configuration behavior (e.g., `System.getProperty("log4j.configurationFile")`, `System.getProperty("log4j.configuration")`, or similar property-based config overrides)
- THEN the TG should write a test that:
  1. **Sets the system property** explicitly before invoking the configuration method using `System.setProperty("propertyName", "value")`
  2. **Calls the configuration method** that reads the property (e.g., `Configurator.initialize("name", null)` or similar)
  3. **Asserts that the returned configuration uses the expected resource**, not the default one — by checking configuration name, source location, or specific configuration elements
  4. **Cleans up** the system property in a `@After` or `finally` block to avoid polluting other tests

- The test should verify that the system property actually takes effect and overrides the default behavior. Without explicitly setting the property, the test may inadvertently rely on environment-specific defaults, leading to false passes or failures.

- Common pitfalls to avoid:
  - **Only testing default behavior** — e.g., calling `Configurator.initialize("name", null)` without setting a system property and only verifying a non-null configuration is returned
  - **Not isolating the system property change** — other tests may set or clear the same property, causing flaky behavior
  - **Testing with an empty/null property value** — the bug occurs when the property is set to a valid resource path, but the code ignores it and returns the default

### Correct Example (catches the bug):
```java
@Test
public void testFromClassPathProperty() throws Exception {
    System.setProperty("log4j.configurationFile", "classpath:TestConfigurator.xml");
    try {
        final Configuration config = Configurator.initialize(null, "TestConfigurator");
        assertNotNull("No configuration returned", config);
        assertEquals("Incorrect Configuration", "ConfigTest", config.getName());
    } finally {
        System.clearProperty("log4j.configurationFile");
    }
}
```

### Incorrect Example (misses the bug):
```java
@Test
public void testInitialize() {
    Configuration config = Configurator.initialize("TestConfigurator", null);
    assertNotNull(config);
    // Does not test system property override — will pass even if
    // the code ignores the log4j.configurationFile property
}
```