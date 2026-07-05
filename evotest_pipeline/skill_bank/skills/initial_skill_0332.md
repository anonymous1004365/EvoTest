---
name: plugin-realm-cache-key-mutation
description: WHEN the TG sees a plugin realm cache that uses a mutable key object
  (e.g., PluginRealmCache.Key) with fields that can change after cache insertion,
  THEN it should test that cache lookups correctly distinguish records despite field
  mutations on the key object, verifying that state mutation does not corrupt cache
  behavior.
code_tags:
- STATE_MUTATION
- RESOURCE_MANAGEMENT
- VALIDATION
- PLUGIN_CACHE_KEY_EQUALS
test_pattern: STATE_TEST
---

# plugin-realm-cache-key-mutation

## Instructions

# Plugin Realm Cache Key Mutation

## Instructions

- WHEN the TG encounters a plugin realm cache implementation (e.g., `DefaultPluginRealmCache`) where the cache key is a mutable object (e.g., `PluginRealmCache.Key`) with fields like `workspace`, `plugin`, `dependencyFilter`, and the key class defines custom `equals()`/`hashCode()` using those fields
- THEN the TG should write a test that:
  1. Creates a mutable key object (e.g., `PluginRealmCache.Key key = new PluginRealmCache.Key(...)`)
  2. Obtains a plugin realm from the cache using that key (via `getPluginRealm`)
  3. **Mutates a field on the same key object** (e.g., `key.setWorkspace(...)` or change `plugin.getArtifactId()`)
  4. Obtains a plugin realm from the cache again using the *mutated* key
  5. **Verifies that the cache correctly returns a different/new record** for the mutated key (i.e., `assertNotNull` for the mutated key lookup, expecting the cache to treat it as a distinct entry)
  6. Verifies that the original key still returns the original cached record

- Common pitfalls to avoid:
  - Testing only with immutable keys or key objects that are never mutated after insertion — this hides the bug
  - Forgetting to mutate the object *after* the first cache lookup and *before* the second lookup
  - Writing a test that only checks `assertEquals` on the cache size or cache statistics, instead of directly checking that the mutated key returns the expected distinct record
  - Assuming the cache uses a defensive copy of the key — when it does not, mutation corrupts subsequent lookups

**Correct example** (pseudocode):
```java
PluginRealmCache cache = lookup(PluginRealmCache.class);
PluginRealmCache.Key key = new PluginRealmCache.Key(workspace, plugin, dependencyFilter);

// First lookup
ClassRealm realm1 = cache.get(session, pluginDescriptor, ...);
assertNotNull(realm1);

// Mutate the key's plugin descriptor (or workspace)
plugin.setArtifactId("changed");

// Second lookup with mutated key — should return a different record or null
ClassRealm realm2 = cache.get(session, pluginDescriptor, ...);
assertNotNull("Mutated key should produce a distinct cache entry", realm2);
assertNotSame("Mutated key entry should differ from original", realm1, realm2);
```

**Incorrect example** (pseudocode):
```java
PluginRealmCache.Key key = new PluginRealmCache.Key(workspace, plugin, dependencyFilter);
ClassRealm realm1 = cache.get(session, pluginDescriptor, ...);
// Skipping mutation — both lookups use identical key
ClassRealm realm2 = cache.get(session, pluginDescriptor, ...);
assertEquals(realm1, realm2); // Only tests that same key returns same record
```