---
name: managed-resource-annotation-description-validation
description: WHEN the TG encounters code that uses the @ManagedResource annotation
  to register MBeans for JMX management, THEN it should verify that the annotation's
  'description' field preserves its exact value in the registered MBean ObjectName.
  Without validation here, the description can be silently dropped, making MBeans
  unresolvable by their expected names.
code_tags:
- STATE_MUTATION
- TYPE_CONVERSION
- VALIDATION
test_pattern: STATE_TEST
---

# managed-resource-annotation-description-validation

## Instructions

# Managed Resource Annotation Description Validation

## Instructions

- WHEN the TG encounters a class annotated with `@ManagedResource(description = "...")` OR code that registers MBeans using annotation-based managed resource descriptors
- THEN it should write a test that creates a bean instance with the annotation, registers it with the `ManagementStrategy` or `MBeanServer`, and verifies the resulting MBean's `ObjectName` contains the description value (e.g., `description=MyManagedBean`). Failure to include the description in the ObjectName indicates the annotation processing logic dropped it.
- For example, given a bean class `MyManagedBean` annotated with `@ManagedResource(description = "MyManagedBean")`, the test should: (1) Create a `DefaultCamelContext` and enable JMX management; (2) Register the bean via `managementStrategy.manageObject(myBean)`; (3) Query the MBeanServer for an ObjectName matching the description pattern; (4) Assert that the MBean is found (i.e., `assertNotNull(mbeanServer.queryNames(...))` or assert no exception is thrown when resolving the ObjectName).
- Common pitfalls to avoid: (a) Testing only that the bean is registered at all without checking the ObjectName structure — the bug is that the `description` field is silently missing from the ObjectName, making the MBean unresolvable; (b) Assuming that simply not throwing an exception means the MBean is properly registered — the TG must explicitly verify the MBean is findable via its description-based ObjectName; (c) Forgetting to enable JMX in the Camel context (e.g., `context.setManagementName("#managed#")`) before registering managed objects; (d) Writing the test against a mock MBeanServer rather than the real one where the ObjectName construction issue actually manifests.
- **Correct example** (catches the bug):
  ```java
  @Test
  public void testManagedResourceAnnotation() throws Exception {
      // Create context with JMX enabled
      DefaultCamelContext context = new DefaultCamelContext();
      context.disableJMX = false;
      context.setManagementName("#managed#");
      context.init();
      
      // Create and register a managed bean with @ManagedResource(description = "MyManagedBean")
      MyManagedBean bean = new MyManagedBean();
      context.getManagementStrategy().manageObject(bean);
      
      // Query MBeanServer for an ObjectName containing the description
      ObjectName query = new ObjectName("org.apache.camel:type=MyManagedBean,*");
      Set<ObjectName> names = context.getManagementStrategy().getManagementAgent().getMBeanServer().queryNames(query, null);
      
      // BUGGY VERSION FAILS: the description "MyManagedBean" is missing from ObjectName, so query returns empty set
      assertNotNull("MBean should be registered", names);
      assertFalse("MBean ObjectName should contain description", names.isEmpty());
  }
  ```
- **Incorrect example** (misses the bug):
  ```java
  @Test
  public void testManagedResourceAnnotation() throws Exception {
      // This only checks no exception is thrown — insufficient
      DefaultCamelContext context = new DefaultCamelContext();
      context.disableJMX = false;
      MyManagedBean bean = new MyManagedBean();
      context.getManagementStrategy().manageObject(bean); // no exception, but MBean is broken
      // No assertion to verify the MBean is actually findable
  }
  ```
- On the **buggy version** of the code, the test above should fail with an assertion error (empty set from `queryNames`), because the annotation processor drops the `description` field from the ObjectName. On the **fixed version**, the test passes because the description is properly included in the ObjectName.