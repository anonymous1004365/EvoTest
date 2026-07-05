---
name: post-delegation-classloader-creation
description: When a classloader is created without post-delegation mode, tests must
  verify that parent-first delegation works correctly by checking that classes available
  in the parent are loaded from the parent, not the child. This skill applies to any
  VFS classloader creation using preDelegation=false.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- BOUNDARY_CHECK
- CLASS_LOADER_DELEGATION
- VALIDATION
test_pattern: STATE_TEST
---

# post-delegation-classloader-creation

## Instructions

# Post-Delegation ClassLoader Creation

## Instructions

- WHEN the TG encounters code that creates a classloader with `preDelegation=false` (meaning post-delegation mode, where the parent is checked before the child), THEN the TG should write a test that verifies a class available in the parent classloader is actually loaded from the parent, not the child classloader.

- WHEN the TG encounters `AccumuloReloadingVFSClassLoader` or `PostDelegatingVFSClassLoader` being instantiated with a `ContextConfig` whose `preDelegation` field is `false`, THEN the TG should verify the delegation behavior by attempting to load a class that exists in the parent but not in the child's URIs, and asserting the loaded class is the same as one loaded directly from the parent.

- WHEN writing such a test, the TG should create a mock or real parent classloader containing a known class, create a child classloader with `preDelegation=false`, attempt to load the known class via the child, and assert that `child.loadClass("known.Class")` returns the same instance as `parent.loadClass("known.Class")`.

- Common pitfalls to avoid:
  - Only testing with `preDelegation=true` (default) and not testing the `preDelegation=false` path.
  - Not verifying that the loaded class actually came from the parent (e.g., by comparing class objects or checking classloader identity).
  - Assuming post-delegation works correctly without explicitly testing it, since the delegation behavior is inverted from the standard Java classloader model.
  - Not providing the `ContextConfig` with `preDelegation=false` explicitly in the test setup.

### Example (correct):
```java
@Test
public void testPostDelegation() {
  // Create a parent classloader with a known class
  ClassLoader parent = new URLClassLoader(new URL[]{}, null) {
    @Override
    public Class<?> loadClass(String name) throws ClassNotFoundException {
      if ("com.example.TestClass".equals(name)) {
        return byteArrayToClass(/* ... */);
      }
      return super.loadClass(name);
    }
  };
  
  // Create ContextConfig with preDelegation=false
  ContextConfig config = new ContextConfig("file:///some/uri", false);
  
  // Create the classloader under test
  AccumuloReloadingVFSClassLoader loader = new AccumuloReloadingVFSClassLoader(
    config.uris, vfs, parent, config.preDelegation);
  
  // Verify the class is loaded from the parent
  Class<?> loaded = loader.loadClass("com.example.TestClass");
  Class<?> expected = parent.loadClass("com.example.TestClass");
  assertSame("Class should be loaded from parent in post-delegation mode", expected, loaded);
}
```

### Example (incorrect — not checking delegation):
```java
@Test
public void testPostDelegation() {
  ContextConfig config = new ContextConfig("file:///some/uri", false);
  // Only verifies classloader creation, not delegation behavior
  assertNotNull(config);
  // Missing: actual class loading test that proves parent is checked first
}
```