---
name: configuration-state-null-check
description: When a Configuration object is conditionally returned from a reconfigure()
  method, the TG must test that the method correctly handles both null and non-null
  configuration results by checking state only after verifying the config is non-null.
code_tags:
- NULL_CHECK
- VALIDATION
- CONFIG_STATE_NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# configuration-state-null-check

## Instructions

# Configuration State Null Check

## Instructions

- WHEN the TG encounters a `reconfigure()` method that constructs a new Configuration object (e.g., via a factory `factory.getConfiguration(loggerContext, source)`) and then checks the configuration's state (e.g., `config.getState() != State.INITIALIZING`)
- THEN it MUST test that the method handles a null Configuration object without throwing a NullPointerException. The return expression pattern is typically `return config == null || config.getState() != State.INITIALIZING ? null : config;` — the null check protects `getState()` from being called on null. The TG should verify that when `config` is null, the method returns `null` gracefully.
- Include concrete values: use `ConfigurationSource.resetInputStream()` that returns `null` to force the factory to receive a source that leads to null config, or test with a mock that returns null from the factory. Expect that no NullPointerException is thrown when `config` is null.
- Common pitfalls: (1) Testing only the non-null configuration path without testing the null case; (2) Assuming `getState()` is safe to call without checking for null first; (3) Not testing the full `reconfigure()` flow including factory invocation through the actual file or stream path.

**Correct approach (testing the null path):**
```java
// Test that when factory returns null, reconfigure() gracefully returns null
ConfigurationSource source = /* source that causes null config */;
PropertiesConfiguration config = new PropertiesConfiguration(loggerContext, source, rootComponent);
Configuration result = config.reconfigure();
assertNull("Expected null when reconfigure fails", result);
// No NullPointerException should occur
```

**Incorrect approach (missing null Config test):**
```java
// BAD: Only tests the happy path, assumes getState() is always safe
ConfigurationSource source = getValidSource();
PropertiesConfiguration config = new PropertiesConfiguration(loggerContext, source, rootComponent);
Configuration result = config.reconfigure();
// Never tests what happens when config object itself is null
// Misses the NullPointerException bug entirely
```