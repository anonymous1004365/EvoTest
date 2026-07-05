---
name: prefix-property-filtering-ignores-added-properties
description: When a ClientConfiguration.getAllPropertiesWithPrefix method iterates
  over inherited properties but creates a new map from those inherited values only
  after iteration completes, properties added to the config after the config merges
  inherited properties may be silently omitted. Use this skill to write a test that
  adds a custom property to a ClientConfiguration, then verifies getAllPropertiesWithPrefix
  returns it.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# prefix-property-filtering-ignores-added-properties

## Instructions

# Prefix Property Filtering Ignores Added Properties

## Instructions

- WHEN the TG encounters a `getAllPropertiesWithPrefix(ClientProperty)` method on `ClientConfiguration` that iterates inherited properties into a new `HashMap<String,String>` but may not re-fetch properties from the underlying config after the initial map construction
- THEN the TG should:
  1. Create a `ClientConfiguration` object (e.g., `ClientConfiguration cfg = new ClientConfiguration()`)
  2. Set a property within the prefix of interest BEFORE calling `getAllPropertiesWithPrefix`, e.g., `cfg.setProperty(ClientProperty.INSTANCE_ZK_TIMEOUT, "30s")` — note that `INSTANCE_ZK_TIMEOUT` is under the `instance.` prefix
  3. Call `cfg.getAllPropertiesWithPrefix(ClientProperty.INSTANCE_ZK_TIMEOUT)` and assert the returned map is **not empty** and contains the expected key (e.g., `instance.zookeeper.timeout`)
  4. Then **add a new property** after the first call, e.g., `cfg.setProperty(ClientProperty.INSTANCE_ZOOKEEPERS, "localhost")`
  5. Call `getAllPropertiesWithPrefix` again **on the same instance** and verify the newly added property is also present in the result
  6. The test must fail on the buggy version (returning an empty map or missing the newly added property) and pass on the fixed version

- Common pitfalls:
  - **Testing only with String keys/values**: The prefix method expects `ClientProperty` enum values, not raw strings. Use `ClientProperty.INSTANCE_*` constants.
  - **Starting from a config that already loads properties from a file**: `ClientConfiguration` can load from `accumulo-client.properties`. If properties are loaded from file, the bug might be masked because inherited properties already include some values. Always use a **fresh, empty** `ClientConfiguration` for the test that adds properties.
  - **Not cleaning up the map between calls**: When calling `getAllPropertiesWithPrefix` multiple times on the same object, the returned map should reflect the latest config state, not a cached snapshot.
  - **Asserting on the wrong ClientProperty prefix**: Ensure the prefix you pass matches the property you set (e.g., `INSTANCE_ZK_TIMEOUT` has prefix `instance.` so using `INSTANCE_ZOOKEEPERS` also works as both have `instance.` prefix).

### Correct example (verifies newly added properties are returned):

```java
ClientConfiguration config = new ClientConfiguration();
config.setProperty(ClientProperty.INSTANCE_ZK_TIMEOUT, "30s");
Map<String,String> props1 = config.getAllPropertiesWithPrefix(ClientProperty.INSTANCE_ZK_TIMEOUT);
assertFalse("Initial properties should contain instance.zookeeper.timeout", props1.isEmpty());
assertTrue(props1.containsKey("instance.zookeeper.timeout"));
assertEquals("30s", props1.get("instance.zookeeper.timeout"));

// Now add a second property and verify it shows up
config.setProperty(ClientProperty.INSTANCE_ZOOKEEPERS, "localhost");
Map<String,String> props2 = config.getAllPropertiesWithPrefix(ClientProperty.INSTANCE_ZK_TIMEOUT);
assertTrue("Newly added property should appear", props2.containsKey("instance.zookeepers"));
assertEquals("localhost", props2.get("instance.zookeepers"));
```

### Incorrect example (only tests initial load, misses the bug):

```java
ClientConfiguration config = new ClientConfiguration();
config.setProperty(ClientProperty.INSTANCE_ZK_TIMEOUT, "30s");
Map<String,String> props = config.getAllPropertiesWithPrefix(ClientProperty.INSTANCE_ZK_TIMEOUT);
// Only checking the first call — this would pass even on the buggy version
assertFalse(props.isEmpty());
```