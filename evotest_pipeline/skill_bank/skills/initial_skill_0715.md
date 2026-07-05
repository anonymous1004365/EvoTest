---
name: mbean-proxy-null-safety
description: When using JMX.newMBeanProxy to create a proxy for a ManagedCamelContextMBean
  (or similar management interface) obtained from an uninitialized/no-arg Camel context,
  verify that null-safe proxies are created using JMX.newMBeanProxy(mbeanServer, on,
  interface, true) to avoid IllegalArgumentException on method invocations. The skill
  applies to any test that creates a CamelContext via newInstance() without management
  configuration and then attempts to create a proxy for it.
code_tags:
- NULL_CHECK
- VALIDATION
- RESOURCE_MANAGEMENT
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# mbean-proxy-null-safety

## Instructions

# MBean Proxy Null-Safety for Uninitialized Management Objects

## Instructions

- WHEN the TG encounters code that creates a `CamelContext` via `new DefaultCamelContext()` (no-arg constructor) and then retrieves an `ObjectName` via `context.getManagementName()` or `getManagementStrategy().getManagementAgent()` to create a JMX proxy using `JMX.newMBeanProxy(mbeanServer, on, SomeMBeanInterface.class)`.
- THEN the TG MUST write a test that exercises a method on the proxy that would fail if the underlying MBean object has not been registered yet, and expect an `IllegalArgumentException` (or a cause chain ending in `NullPointerException` wrapped as `IllegalArgumentException`) on the buggy version.
- Specifically, the test should call `JMX.newMBeanProxy(mbeanServer, objectName, ManagedCamelContextMBean.class)` without the fourth boolean parameter `true` (notification support), and then invoke a method like `getState()` on it to trigger the exception.
- The correct/fixed behavior is to use `JMX.newMBeanProxy(mbeanServer, objectName, ManagedCamelContextMBean.class, true)`, which makes the proxy null-safe, preventing `IllegalArgumentException` on method invocations where the underlying MBean is not yet fully registered.
- Common pitfalls to avoid:
  - ❌ Testing only that the proxy object is non-null (this passes on both buggy and fixed versions since the proxy itself is always created).
  - ❌ Forgetting to invoke an actual method on the proxy — the bug only manifests at call time, not proxy creation time.
  - ❌ Assuming `context.start()` or route addition will help — the issue occurs even after `start()` if the MBean server registration hasn't completed for the specific MBean being proxied.
  - ✅ Instead, invoke a real method like `getState()` or `getCamelId()` on the proxy and assert that no exception is thrown on the fixed version.

### Example (Correct test approach)

**Test that detects the bug:**
```java
// Buggy version: IllegalArgumentException on proxy method invocation
// Fixed version: null-safe proxy, works fine
ManagedCamelContextMBean proxy = JMX.newMBeanProxy(mbeanServer, on, ManagedCamelContextMBean.class);
try {
    String state = proxy.getState();
    fail("Should throw IllegalArgumentException on buggy version");
} catch (IllegalArgumentException e) {
    // Expected — the MBean was not properly registered for this context
}
```

**Test for fixed version (null-safe proxy):**
```java
// Use the 4-parameter overload with notification support = true
ManagedCamelContextMBean proxy = JMX.newMBeanProxy(mbeanServer, on, ManagedCamelContextMBean.class, true);
// No exception — null-safe
String state = proxy.getState();
```

### Incorrect approach (does not catch the bug)
```java
// This does NOT exercise the proxy methods — passes on both versions
ManagedCamelContextMBean proxy = JMX.newMBeanProxy(mbeanServer, on, ManagedCamelContextMBean.class);
assertNotNull(proxy); // Always passes, does not catch the bug
```