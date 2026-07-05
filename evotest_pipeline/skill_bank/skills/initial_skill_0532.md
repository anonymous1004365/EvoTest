---
name: async-logger-config-include-location-default
description: When a subclass overrides configuration properties from its parent, the
  default value of those properties can differ from the parent's default. This skill
  teaches the TG to test that factory-created async loggers respect the async-specific
  default (includeLocation=false) rather than inheriting the synchronous default (includeLocation=true).
code_tags:
- NULL_CHECK
- STATE_MUTATION
- ARGUMENT_VALIDATION
- PROPERTY_DEFAULT_VALUES
- INHERITANCE_CONFIGURATION
test_pattern: STATE_TEST
---

# async-logger-config-include-location-default

## Instructions

# Async Logger Config — IncludeLocation Default Override

## Instructions

WHEN the TG encounters a class that extends `LoggerConfig` (e.g., `AsyncLoggerConfig`) and overrides behavior by:
- Having its own `@PluginFactory` `createLogger(...)` method, OR
- Having its own `RootLogger` inner class with a `createLogger(...)` factory, OR
- The parent `LoggerConfig` has a field `private boolean includeLocation = true` (default is `true`), AND
- The Javadoc of the subclass states that `includeLocation` should default to `false` for async loggers

THEN the TG should:
1. **Create a test that explicitly calls the factory method(s) with `null` for the `includeLocation` parameter** — this simulates the user omitting the attribute in configuration
2. **Assert that `isIncludeLocation()` returns `false`** for the created `LoggerConfig` instance
3. **Test BOTH the async root logger** (`AsyncLoggerConfig.RootLogger.createLogger(...)`) **AND the async named logger** (`AsyncLoggerConfig.createLogger(...)`)
4. **Use a real `DefaultConfiguration` object** as the `Configuration` parameter, not a mock — because `AsyncLoggerConfig` internally calls `config.getAsyncLoggerConfigDelegate()` which requires a real configuration
5. **Pass `null` for all simple-type string attributes** (additivity, level, name, includeLocation) and **empty arrays for `AppenderRef[]`** and **`null` for Filter** to keep the test focused on the includeLocation default

**What the test should verify:**
- `AsyncLoggerConfig.RootLogger.createLogger(...)` with `includeLocation=null` → produces a LoggerConfig with `isIncludeLocation() == false`
- `AsyncLoggerConfig.createLogger(...)` with `includeLocation=null` → produces a LoggerConfig with `isIncludeLocation() == false`

**What to expect on the buggy version:**
The buggy version of `LoggerConfig.includeLocation(String)` method returns `true` when the config value is `null` (line 530: `if (includeLocationConfigValue == null) { return true; }`). This means async loggers incorrectly default to `includeLocation=true` instead of the documented `includeLocation=false`.

**Common pitfalls to avoid:**
- **Testing only synchronous LoggerConfig**: The synchronous logger correctly defaults to `includeLocation=true`. The bug is specific to asynchronous loggers. Always test `AsyncLoggerConfig` and its `RootLogger`.
- **Using `List.of()` or `Arrays.asList()` for appenderRefs**: The constructor expects `List<AppenderRef>`, but passing an empty list like `new AppenderRef[0]` as the array and then calling `Arrays.asList(...)` internally works. Use `new AppenderRef[0]` directly.
- **Mocking Configuration**: `AsyncLoggerConfig` constructor calls `config.getAsyncLoggerConfigDelegate()` which returns a real delegate from the configuration. Using a mock will cause NPE. Always use `new DefaultConfiguration()`.
- **Testing only one factory method**: The bug affects both `AsyncLoggerConfig.createLogger()` and `AsyncLoggerConfig.RootLogger.createLogger()`. Both must be tested.
- **Passing `"false"` string instead of `null`**: The test must pass `null` for `includeLocation` to verify the default behavior. Passing `"false"` explicitly tests explicit configuration, not the default.

### Correct Example (from the actual test)

```java
@Test
public void testIncludeLocationDefaultsToFalse() {
    final LoggerConfig rootLoggerConfig =
            AsyncLoggerConfig.RootLogger.createLogger(
                    null, "INFO", null, new AppenderRef[0], null, new DefaultConfiguration(), null);
    assertFalse("Include location should default to false for async loggers",
                rootLoggerConfig.isIncludeLocation());

    final LoggerConfig loggerConfig =
            AsyncLoggerConfig.createLogger(
                    null, "INFO", "com.foo.Bar", null, new AppenderRef[0], null, new DefaultConfiguration(),
                    null);
    assertFalse("Include location should default to false for async loggers",
                loggerConfig.isIncludeLocation());
}
```

### Incorrect Example (pitfall)

```java
// WRONG: testing synchronous LoggerConfig instead of AsyncLoggerConfig
@Test
public void testIncludeLocationDefaults() {
    // This would pass even on the buggy version because synchronous defaults correctly
    LoggerConfig loggerConfig = LoggerConfig.createLogger(
        null, "INFO", "test", null, null, null, new DefaultConfiguration(), null);
    assertTrue(loggerConfig.isIncludeLocation()); // true is expected for sync
}
```

```java
// WRONG: using a mock Configuration
@Test
public void testIncludeLocationDefaultsToFalse() {
    Configuration mockConfig = mock(Configuration.class);
    // This will throw NPE because getAsyncLoggerConfigDelegate() returns null
    LoggerConfig loggerConfig = AsyncLoggerConfig.createLogger(
        null, "INFO", "test", null, new AppenderRef[0], null, mockConfig, null);
}
```