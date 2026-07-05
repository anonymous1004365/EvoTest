---
name: plugin-realm-cache-equality
description: When a PluginRealmCache uses a cache key whose hashCode depends only
  on constructor-time fields but equals also compares fields that can be mutated after
  creation (e.g., Plugin's dependencies list), a false cache hit can cause put() to
  throw IllegalStateException for "Duplicate plugin realm". Test by loading the same
  plugin with identical parameters in two separate calls and verifying the second
  call succeeds.
code_tags:
- NULL_CHECK
- EXCEPTION_HANDLING
- VALIDATION
- CACHE_KEY_EQUALS_HASHCODE
- STATE_MUTATION
test_pattern: STATE_TEST
---

# plugin-realm-cache-equality

## Instructions

# Plugin Realm Cache Equality Consistency

## Instructions

- WHEN the TG encounters a `PluginRealmCache` implementation (e.g., `DefaultPluginRealmCache`) where the cache key's `hashCode()` is computed eagerly in the constructor using fields that include `Plugin.getDependencies()` (via `CacheUtils.pluginHashCode()`), but the `Plugin` object's dependency list (`getDependencies()`) can be **mutated after the cache key is created** (e.g., by setting dependencies on the `Plugin` object that was cloned, where `Plugin.clone()` creates a shallow copy sharing the same `List<Dependency>` reference)

- THEN the TG should write a test that:
  1. Creates a `Plugin` with specific groupId, artifactId, and version (e.g., `"org.apache.maven.plugins"`, `"maven-jar-plugin"`, `"2.4"`)
  2. Creates a `MavenSession` and a `RepositorySystemSession` using the test framework (e.g., `AbstractCoreMavenComponentTestCase.createMavenSession(null)`)
  3. Obtains the `PluginRealmCache` instance (e.g., via `lookup(PluginRealmCache.class)`)
  4. Creates the first cache `Key` using `cache.createKey(plugin, ...)` and calls `cache.put(key, pluginRealm, pluginArtifacts)` — this should succeed
  5. **Then mutates the plugin's dependency list** (e.g., `plugin.getDependencies().add(new Dependency())`) — this simulates what happens in production when a plugin's dependencies are resolved and set after key creation
  6. Creates a **second** cache `Key` using `cache.createKey(plugin, ...)` with the same `Plugin` object (now mutated)
  7. Calls `cache.put(secondKey, differentPluginRealm, differentPluginArtifacts)`
  8. **Verifies** that the second `put()` call **succeeds** (i.e., does NOT throw `IllegalStateException` with message containing "Duplicate plugin realm")

- The test should verify that:
  - The two `Key` objects are **not equal** (`assertFalse(key1.equals(key2))`)
  - Their `hashCode()` values are **different** (since the dependencies changed, the hash should differ)
  - The cache retains both entries (e.g., `cache.get(key1)` returns first record, `cache.get(key2)` returns second record)

- Common pitfalls to avoid:
  - Testing only with plugins that have no dependencies — the bug only manifests when dependencies differ between calls
  - Using `Plugin.clone()` and expecting a deep copy — `Plugin.clone()` in the Maven model creates a shallow copy, so the cloned Plugin and original share the same `dependencies` List reference
  - Assuming `hashCode()` is computed dynamically — in `DefaultPluginRealmCache.CacheKey`, `hashCode` is computed once in the constructor and cached, so if the `Plugin` is mutated after key creation, `equals()` may return `true` (because it compares the mutated fields) but the second key's `hashCode` may differ from the first's (since it was computed after mutation), leading to inconsistent behavior: the second `put()` finds no collision in the `ConcurrentHashMap` (different hash buckets), but a future `get()` using one of the keys may find nothing because the keys compare unequally
  - Forgetting that the bug can also manifest as a **cache miss** (expected cache hit returns null) rather than just a "duplicate plugin realm" exception

## Example: Correct Test Approach

```java
// Correct: mutates plugin between two cache key creations
Plugin plugin = new Plugin();
plugin.setGroupId("org.apache.maven.plugins");
plugin.setArtifactId("maven-jar-plugin");
plugin.setVersion("2.4");

MavenSession session = createMavenSession(null);
RepositorySystemSession repoSession = session.getRepositorySession();
PluginRealmCache cache = (PluginRealmCache) lookup(PluginRealmCache.class);

// First key — no dependencies yet
Key key1 = cache.createKey(plugin, ...);
CacheRecord record1 = new CacheRecord(realm1, artifacts1);
cache.put(key1, realm1, artifacts1);

// Now simulate what happens in DefaultMavenPluginManager:
// plugin dependencies are resolved and set after key creation
plugin.getDependencies().add(new Dependency());

// Second key — dependencies now present
Key key2 = cache.createKey(plugin, ...);
assertFalse("Keys should be different after dependency mutation", key1.equals(key2));
CacheRecord record2 = new CacheRecord(realm2, artifacts2);
// This should NOT throw IllegalStateException
cache.put(key2, realm2, artifacts2);
```

## Example: Incorrect Test Approach (would miss the bug)

```java
// Incorrect: creates two separate Plugin objects — doesn't test mutation scenario
Plugin plugin1 = new Plugin();
plugin1.setGroupId("org.apache.maven.plugins");
plugin1.setArtifactId("maven-jar-plugin");
plugin1.setVersion("2.4");

Plugin plugin2 = new Plugin();
plugin2.setGroupId("org.apache.maven.plugins");
plugin2.setArtifactId("maven-jar-plugin");
plugin2.setVersion("2.4");
plugin2.getDependencies().add(new Dependency());

// This tests two unrelated Plugin objects, not the mutation path
Key key1 = cache.createKey(plugin1, ...);
Key key2 = cache.createKey(plugin2, ...);
```