---
name: zookeeper-host-argument-propagation
description: When constructing an object that passes ZooKeeper host strings to a ZooCacheFactory,
  ensure that the complete multi-host comma-separated string is propagated to getZooCache.
  The TG should verify that all ZooKeeper hosts in the configuration are actually
  used by the cache layer.
code_tags:
- BOUNDARY_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: INTERACTION_TEST
---

# zookeeper-host-argument-propagation

## Instructions

# ZooKeeper Host Argument Propagation

## Instructions

- WHEN the TG sees a class (e.g. `ZooKeeperInstance`) that reads a ZooKeeper host list from configuration (e.g. `ClientProperty.INSTANCE_ZK_HOST`) and passes it to a `ZooCacheFactory.getZooCache(...)` call
- THEN the TG should write an interaction test using a mock `ZooCacheFactory` to verify the exact string value passed to `getZooCache`. The test must:
  1. Create a `ClientConfiguration` with a **multi-host** ZooKeeper string (e.g. `"zk1,zk2,zk3"`) via `.withZkHosts(...)`.
  2. Mock `ZooCacheFactory` and expect a call to `getZooCache(hostString, timeout)` where `hostString` is the **exact multi-host string** (e.g. `"zk1,zk2,zk3"`), not a subset or single host.
  3. Assert that the instance's `getZooKeepers()` method returns the **same multi-host string** that was configured.
  4. Assert that the instance's `getInstanceName()` returns the configured instance name.

- WHEN the TG writes such a test, it MUST:
  - Use a `ZooCacheFactory` mock (EasyMock `createMock(ZooCacheFactory.class)`).
  - Set up expectations: `expect(factory.getZooCache(zookeepers, timeout)).andReturn(zc).anyTimes()` where `zookeepers` is the exact multi-host string.
  - Replay the mock, construct the object with the mock factory, then verify the getters.
  - Include the instance name verification as a secondary assertion.

- Common pitfalls to avoid:
  - ❌ Testing with only a single host string (e.g. `"zk1"`) — this would not catch the bug where only the first host is used.
  - ❌ Not verifying the `getZooKeepers()` getter output — the bug may affect the getter return value.
  - ❌ Using a real `ZooCacheFactory` or real `ZooCache` instead of mocks, which would require an actual ZooKeeper connection.
  - ❌ Forgetting to set up the `getZooCache` expectation with `.anyTimes()` — the constructor may call the method multiple times.

### Correct Example

```java
@Test
public void testAllZooKeepersAreUsed() {
    final String zookeepers = "zk1,zk2,zk3", instanceName = "accumulo";
    ZooCacheFactory factory = createMock(ZooCacheFactory.class);
    ZooCache zc = createMock(ZooCache.class);
    expect(factory.getZooCache(zookeepers, 30000)).andReturn(zc).anyTimes();
    expect(zc.get(Constants.ZROOT + Constants.ZINSTANCES + "/" + instanceName))
        .andReturn(IID_STRING.getBytes(UTF_8));
    expect(zc.get(Constants.ZROOT + "/" + IID_STRING)).andReturn("yup".getBytes());
    replay(zc, factory);
    ClientConfiguration cfg = ClientConfiguration.loadDefault()
        .withInstance(instanceName).withZkHosts(zookeepers);
    ZooKeeperInstance zki = new ZooKeeperInstance(cfg, factory);
    assertEquals(zookeepers, zki.getZooKeepers());
    assertEquals(instanceName, zki.getInstanceName());
}
```

### Incorrect Example (would not catch the bug)

```java
@Test
public void testZooKeeperHost() {
    // BUG: Only uses a single host — would not detect if multi-host is truncated
    ZooCacheFactory factory = createMock(ZooCacheFactory.class);
    ZooCache zc = createMock(ZooCache.class);
    expect(factory.getZooCache("zk1", 30000)).andReturn(zc).anyTimes();
    expect(zc.get(anyString())).andReturn(IID_STRING.getBytes(UTF_8));
    replay(zc, factory);
    ClientConfiguration cfg = ClientConfiguration.loadDefault()
        .withInstance("accumulo").withZkHosts("zk1");
    ZooKeeperInstance zki = new ZooKeeperInstance(cfg, factory);
    // Only checks instance name, not the full keeper list
    assertEquals("accumulo", zki.getInstanceName());
}
```