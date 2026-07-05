---
name: mbean-objectname-registration-tracking
description: When an MBeanServer can modify the ObjectName during registration (e.g.,
  WebSphere), the agent must track the actual registered name separately from the
  source name. This skill teaches how to test that isRegistered and unregister use
  the correct mapped ObjectName.
code_tags:
- REGISTRY_CLEANUP_STATE
- JMX_OBJECTNAME_MODIFICATION
- CONCURRENCY
test_pattern: INTERACTION_TEST
---

# mbean-objectname-registration-tracking

## Instructions

# MBean ObjectName Registration Tracking

## Instructions

- WHEN the TG encounters code that registers MBeans via `MBeanServer.registerMBean(Object, ObjectName)` and stores the result in a `ConcurrentMap<ObjectName, ObjectName>` (mapping source names to actual registered names, e.g., `mbeansRegistered`)
- THEN the TG should write a test that:
  1. Creates a mock `MBeanServer` using `mock(MBeanServer.class)` and a mock `ObjectInstance` using `mock(ObjectInstance.class)`
  2. Sets up the mock so that `isRegistered(sourceObjectName)` returns `false`, and `registerMBean(object, sourceObjectName)` returns the mock `ObjectInstance`
  3. Configures `instance.getObjectName()` to return a **different** `ObjectName` (e.g., `registeredObjectName`) than the source `ObjectName`
  4. Calls `agent.register(object, sourceObjectName)`
  5. Verifies that `agent.isRegistered(sourceObjectName)` returns `true` (even though the MBeanServer registered it under a different name)
  6. Then calls `agent.unregister(sourceObjectName)` and verifies that `agent.isRegistered(sourceObjectName)` returns `false`
  7. Verifies that `mbeanServer.unregisterMBean(registeredObjectName)` was called (not `unregisterMBean(sourceObjectName)`)

- CRITICAL: The `isRegistered(ObjectName name)` method in `DefaultManagementAgent` first checks the `mbeansRegistered` map for the name, and if not found there, falls back to `server.isRegistered(name)`. A common pitfall is:
  - **Pitfall 1**: Testing with only one ObjectName (source == registered) — this won't catch the bug because the map lookup succeeds trivially
  - **Pitfall 2**: Not resetting mocks between register and unregister — use `reset(mbeanServer, instance)` after the register verification to reset mock state for the unregister phase
  - **Pitfall 3**: Forgetting to stub `mbeanServer.isRegistered(registeredObjectName)` to return `true` after registration

- The test must use concrete `ObjectName` instances with different values (e.g., `new ObjectName("domain", "key", "value")` vs `new ObjectName("domain", "key", "otherValue")`)

- Example correct approach:
  ```java
  @Test
  public void testObjectNameModification() throws JMException {
      MBeanServer mbeanServer = mock(MBeanServer.class);
      ObjectInstance instance = mock(ObjectInstance.class);
      ManagementAgent agent = new DefaultManagementAgent();
      agent.setMBeanServer(mbeanServer);
      Object object = "object";
      ObjectName sourceObjectName = new ObjectName("domain", "key", "value");
      ObjectName registeredObjectName = new ObjectName("domain", "key", "otherValue");

      when(mbeanServer.isRegistered(sourceObjectName)).thenReturn(false);
      when(mbeanServer.registerMBean(object, sourceObjectName)).thenReturn(instance);
      when(instance.getObjectName()).thenReturn(registeredObjectName);
      when(mbeanServer.isRegistered(registeredObjectName)).thenReturn(true);

      agent.register(object, sourceObjectName);
      assertTrue(agent.isRegistered(sourceObjectName));

      reset(mbeanServer, instance);
      when(mbeanServer.isRegistered(registeredObjectName)).thenReturn(true);
      mbeanServer.unregisterMBean(registeredObjectName);

      agent.unregister(sourceObjectName);
      assertFalse(agent.isRegistered(sourceObjectName));
  }
  ```

- Example incorrect approach (does not catch the bug):
  ```java
  // BAD: uses same ObjectName for source and registered
  ObjectName sameName = new ObjectName("domain", "key", "value");
  when(instance.getObjectName()).thenReturn(sameName);
  // This doesn't exercise the mapping logic — the map lookup
  // succeeds trivially since source == registered
  ```