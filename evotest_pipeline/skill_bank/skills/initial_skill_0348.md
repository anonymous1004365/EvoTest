---
name: plugin-realm-cache-extension-reuse
description: When testing cache-based plugin realm retrieval, verify that cached extension
  realms created during build extension loading are properly retrieved and reused
  when the same plugin's mojos are executed, especially for plugins with extensions=true.
  A common bug is the cache returning null for a plugin that was previously loaded
  as an extension, causing NPE.
code_tags:
- NULL_CHECK
- VALIDATION
- BOUNDARY_CHECK
- CACHING_AND_CONVERTER_REGISTRY
test_pattern: STATE_TEST
---

# plugin-realm-cache-extension-reuse

## Instructions

# Plugin Realm Cache Reuse for Extension Plugins

## Instructions

- WHEN the TG encounters code that uses a `PluginRealmCache` or `ExtensionRealmCache` to create/get `ClassRealm` objects for plugin execution, AND the code distinguishes between build extension loading and mojo execution phases
- THEN the TG should write a test that:
  1. Creates a `MavenSession` with a `MavenProject` that has a build extension plugin (with `extensions=true` in its POM model), and verifies the extension realm is created and cached during `getPluginRealm()` for that plugin
  2. Calls `getPluginRealm()` a second time with the same `PluginDescriptor` (same groupId:artifactId:version), and verifies the returned `ClassRealm` is **not null** — i.e., the cache returns the previously created realm rather than null
  3. Runs the test against the buggy version and expects the second call to return `null` or throw a `NullPointerException` when the calling code tries to use the `ClassRealm` (e.g., `pluginRealm.display(...)`)

- The test should use a `PluginDescriptor` built with `groupId="org.apache.maven.its.plugins"`, `artifactId="maven-it-plugin"`, `version="0.1"`, and `setIsExtension(true)` on the `PluginDescriptor` to simulate a plugin used as a build extension
- The test must use the `BuildPluginManager` interface (from `maven-core`), calling `getPluginRealm(MavenSession, PluginDescriptor)` directly — do NOT mock the `PluginRealmCache`
- **Common pitfall**: Only testing with non-extension plugins or testing only the first call to `getPluginRealm()`. The bug manifests specifically when the same plugin is first loaded as a build extension (which uses `ExtensionRealmCache`) and then later requested as a regular plugin realm (which uses `PluginRealmCache`). Without the fix, the second call returns null because the cache key created during extension loading does not match the key created during mojo execution.
- **Common pitfall**: Using mock objects for `MavenSession` or `MavenProject`. The test must create real or minimally-stubbed sessions and projects, because the cache key computation depends on actual `RepositorySystemSession` attributes like `getLocalRepository()` and `getWorkspace()`.

### Correct Example Structure
```java
// In PluginManagerTest:
@Test
public void testPluginRealmReusedAfterExtensionLoading() throws Exception {
    // Create project with extension plugin
    MavenProject project = new MavenProject();
    Plugin plugin = new Plugin();
    plugin.setGroupId("org.apache.maven.its.plugins");
    plugin.setArtifactId("maven-it-plugin");
    plugin.setVersion("0.1");
    project.getBuild().getExtensions().add(plugin);
    
    // Create session from the project
    MavenSession session = new MavenSession(container, ...);
    session.setCurrentProject(project);
    
    // First call: loads as extension
    ClassRealm realm1 = pluginManager.getPluginRealm(session, pluginDescriptor);
    assertNotNull("First call should create realm", realm1);
    
    // Second call: should reuse cached realm
    ClassRealm realm2 = pluginManager.getPluginRealm(session, pluginDescriptor);
    assertNotNull("Second call should return cached realm, not null", realm2);
    assertSame("Cached realm should be reused", realm1, realm2);
}
```

### Incorrect Example to Avoid
```java
// WRONG: Only testing first call, not verifying cache reuse
@Test
public void testGetPluginRealm() {
    ClassRealm realm = pluginManager.getPluginRealm(session, descriptor);
    assertNotNull(realm);  // Only tests first call — misses the bug
}

// WRONG: Using mocks instead of real objects — won't trigger cache key mismatch
@Test
public void testGetPluginRealmMocked() {
    when(session.getRepositorySession()).thenReturn(mockSession);
    // Mock prevents proper cache key computation
    ...
}
```