---
name: client-config-property-override-verification
description: When a CLI class reads a property (like trace hosts) that can be overridden
  via client configuration, the TG should test that the final configuration correctly
  uses the overridden value rather than a hardcoded default. This skill helps catch
  bugs where property values get lost during config merging.
code_tags:
- NULL_CHECK
- VALIDATION
- CONFIGURATION_RELOAD
test_pattern: PARAMETRIC_TEST
---

# client-config-property-override-verification

## Instructions

# Client Configuration Property Override Verification

## Instructions

- WHEN the TG encounters a class that reads configuration properties from a `ClientConfiguration` (e.g., via `getClientConfiguration()`) and uses those properties to set internal state (e.g., trace hosts, instance name, zoo keeper hosts)
- THEN the TG should write a test that:
  1. Creates a temporary client configuration properties file with a NON-DEFAULT value for the property in question (e.g., `trace.hosts=localhost:45454` instead of the default `localhost:2181`)
  2. Sets the system property that points to this config file (e.g., `accumulo.properties` or `clientConfigFile`)
  3. Calls the method that reads the configuration and extracts the property (e.g., `getClientConfiguration()`)
  4. Verifies that the returned configuration contains the custom value (`localhost:45454`) not the hardcoded default (`localhost:2181`)
- The test should catch bugs where the property is either not read from config at all, or is overwritten by a fallback default value after being read
- Common pitfall: testing only that the class exists or that defaults are present, without verifying that user-provided overrides in config files actually propagate through
- Example correct approach: Create a config file with `trace.hosts=localhost:45454`, point the system to use it, then assert `assertEquals("localhost:45454", shellOptionsJC.getClientConfiguration().get(Property.INSTANCE_ZK_HOST))` (or equivalent property getter)
- Example incorrect approach: Only asserting that `getClientConfiguration()` returns a non-null config, or only checking that the default trace host value is present, without testing override behavior