---
name: late-logger-configuration-reload-check
description: When testing LoggerContext reconfiguration with a URI-based config file,
  the TG should verify that calling getContext(null, false, configFileURI) returns
  a new LoggerContext that has a different Configuration object than the original,
  and that the new Configuration is of type XmlConfiguration (not DefaultConfiguration).
  Also verify that subsequent getContext(false) returns the same updated context.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- CONFIGURATION_RELOAD
test_pattern: STATE_TEST
---

# late-logger-configuration-reload-check

## Instructions

# Late Logger Configuration Reload Check

## Instructions

- WHEN the TG encounters code that obtains a `LoggerContext` via `LoggerContext.getContext(false)`, then later reconfigures it by calling `LoggerContext.getContext(null, false, configFileURI)` (passing `null` as ClassLoader, `false` for currentContext, and a `java.net.URI` from a `File.toURI()`)
- THEN the TG should write a test that:
  1. Obtains an initial `LoggerContext` via `LoggerContext.getContext(false)` and stores its `Configuration` object (obtained via `context.getConfiguration()`).
  2. Asserts the initial configuration is a `DefaultConfiguration` instance using `assertTrue("Not set to default configuration", cfg instanceof DefaultConfiguration)`.
  3. Creates a `File` pointing to a valid test XML config file (e.g., `"target/test-classes/log4j-test1.xml"`), converts it to a URI, and calls `LoggerContext.getContext(null, false, file.toURI())` to trigger reconfiguration.
  4. Asserts the returned `LoggerContext` is not null.
  5. Calls `loggerContext.getConfiguration()` on the returned context and asserts it is a **different object** from the original configuration (use `assertTrue("Configuration not reset", cfg != newConfig)` with `!=` reference comparison).
  6. Asserts the new configuration is an `XmlConfiguration` instance using `assertTrue("Reconfiguration failed", newConfig instanceof XmlConfiguration)`.
  7. Obtains the context again via `LoggerContext.getContext(false)` and asserts it returns the **same** `Configuration` object as the new one (using `assertTrue("Configuration should not have been reset", newConfig == sameConfig)` with `==` reference comparison).
- Common pitfalls to avoid:
  - **Using `.equals()` instead of `==` / `!=`**: The test must use identity checks (`==` and `!=`) on `Configuration` objects in steps 5 and 7, not structural equality checks, because the bug is that the configuration object reference is not properly updated.
  - **Not verifying the original config type**: The test should confirm the initial config is a `DefaultConfiguration` before reconfiguration to establish the baseline.
  - **Not calling `context.getConfiguration()` on the right object**: In step 5, call `getConfiguration()` on the `LoggerContext` returned by `getContext(null, false, ...)`, not on the original `context`.
  - **Forgetting to check that reconfiguration persists**: After reconfiguration, verify that calling `getContext(false)` again still returns the new configuration (step 7) to catch bugs where the configuration is temporarily set but then reverted.
  - **Missing `@BeforeClass`/`@AfterClass` cleanup**: Use `@BeforeClass` to set up the initial context and `@AfterClass` to call `Configurator.shutdown(context)` and `StatusLogger.getLogger().reset()`.

### Correct Example (from LateConfigTest.testReconfiguration)

```java
@BeforeClass
public static void setupClass() {
    context = LoggerContext.getContext(false);
}

@AfterClass
public static void tearDownClass() {
    Configurator.shutdown(context);
    StatusLogger.getLogger().reset();
}    

@Test
public void testReconfiguration() throws Exception {
    final Configuration cfg = context.getConfiguration();
    assertNotNull("No configuration", cfg);
    assertTrue("Not set to default configuration", cfg instanceof DefaultConfiguration);
    final File file = new File(CONFIG);
    final LoggerContext loggerContext = LoggerContext.getContext(null, false, file.toURI());
    assertNotNull("No Logger Context", loggerContext);
    final Configuration newConfig = loggerContext.getConfiguration();
    assertTrue("Configuration not reset", cfg != newConfig);
    assertTrue("Reconfiguration failed", newConfig instanceof XmlConfiguration);
    context = LoggerContext.getContext(false);
    final Configuration sameConfig = context.getConfiguration();
    assertTrue("Configuration should not have been reset", newConfig == sameConfig);
}
```

### Incorrect Example (would miss the bug)

```java
@Test
public void testReconfigurationIncorrect() throws Exception {
    final Configuration cfg = context.getConfiguration();
    // Wrong: Using .equals() instead of !=
    assertFalse("Configuration should be different", cfg.equals(newConfig));
    // Wrong: Not checking the type of the new configuration
    // Wrong: Not verifying that getContext(false) still returns the updated config
}
```