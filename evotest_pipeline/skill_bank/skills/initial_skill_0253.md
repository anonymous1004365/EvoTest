---
name: property-key-existence-check
description: When configuring a MiniAccumuloCluster with random ports, ensure that
  all expected property keys (like monitor.port.log4j) are set in the configuration
  before starting the cluster. The bug arises when a property key is missing from
  the configuration, causing a "Found no value for X" failure.
code_tags:
- PROPERTY_KEY_VALIDATION
- CONFIGURATION_RELOAD
- VALIDATION
test_pattern: STATE_TEST
---

# property-key-existence-check

## Instructions

# Property Key Existence Check in MiniAccumuloCluster Configuration

## Instructions

- WHEN the TG encounters test code that sets random ports on a MiniAccumuloCluster configuration (e.g., calling `setRandomPorts()` on the config)
- THEN the TG should write a test that verifies every property that was configured for random port assignment is actually present in the resulting configuration, specifically for all properties in the list: `Property.TSERV_CLIENTPORT`, `Property.MONITOR_PORT`, `Property.MONITOR_LOG4J_PORT`, `Property.MASTER_CLIENTPORT`, and any other port property passed to `setRandomPorts`
- The test should call `setRandomPorts()` on the `MiniAccumuloConfigImpl`, then for each port property in the set, call `conf.get(property.getKey())` and verify the returned value is non-null (e.g., `assertNotNull("Found no value for " + property.getKey(), value)`)
- The test should be runnable against the buggy version where `MONITOR_LOG4J_PORT` may be missing from the random port property set, causing `conf.get("monitor.port.log4j")` to return null
- Common pitfalls: 
  - Only checking a subset of port properties (e.g., checking only `TSERV_CLIENTPORT` and `MONITOR_PORT` but not `MONITOR_LOG4J_PORT`)
  - Relying on `getPort()` methods instead of checking the raw property keys in the configuration
  - Assuming all port properties are handled uniformly when some may be inadvertently omitted from the random port assignment logic

### Correct Example:
```java
@Test
public void testRandomPorts() {
  MiniAccumuloConfigImpl config = new MiniAccumuloConfigImpl(tmpDir, "password");
  config.setRandomPorts();
  for (Property randomPortProp : new Property[] {Property.TSERV_CLIENTPORT, Property.MONITOR_PORT, 
      Property.MONITOR_LOG4J_PORT, Property.MASTER_CLIENTPORT}) {
    String value = config.getSiteConfiguration().get(randomPortProp.getKey());
    assertNotNull("Found no value for " + randomPortProp.getKey(), value);
  }
}
```

### Incorrect Example:
```java
@Test
public void testRandomPorts() {
  MiniAccumuloConfigImpl config = new MiniAccumuloConfigImpl(tmpDir, "password");
  config.setRandomPorts();
  // Only checking two properties, missing MONITOR_LOG4J_PORT!
  assertNotNull(config.getPort(Property.TSERV_CLIENTPORT));
  assertNotNull(config.getPort(Property.MONITOR_PORT));
}
```