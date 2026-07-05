---
name: plugin-dependency-scope-resolution-validation
description: When resolving plugin dependencies (particularly in DefaultBuildPluginManager),
  always verify that all dependency scopes (compile, runtime, test, system, provided)
  are correctly mapped and resolved. This skill helps test that scope=edge mapping
  is complete and no scope is accidentally omitted.
code_tags:
- VALIDATION
- ARRAY_INDEX_ACCESS
- NULL_CHECK
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# plugin-dependency-scope-resolution-validation

## Instructions

# Plugin Dependency Scope Resolution Validation

## Instructions

### WHEN the TG encounters a method that resolves plugin dependencies or maps dependency scopes:

- WHEN resolving `Plugin` dependencies and their scopes (e.g., `MavenProject.getPluginArtifacts()`, plugin dependency resolution logic in `DefaultBuildPluginManager`)
- THEN the TG should write a test that:
  1. Creates a plugin with dependencies covering **each scope type** that the code handles: `compile`, `runtime`, `test`, `system`, `provided`
  2. Verifies that **every** such dependency is resolved and present in the output collection after scope resolution
  3. Uses assertion methods that check for **all expected artifacts** — not just one or two
  4. Specifically tests a dependency with `scope = "system"`, as this scope is most commonly overlooked or accidentally filtered out

### Concrete test pattern for the actual code:

```java
// Correct test approach:
// - Create a MavenProject with a plugin dependency that has system scope
// - Invoke the method that resolves plugin dependencies
// - Assert the system-scope dependency is in the resolved artifacts list

public void testThatPluginDependencyThatHasSystemScopeIsResolved() throws Exception {
    // Setup: ensure plugin dependency with system scope exists
    // Exercise: resolve plugin dependencies via DefaultBuildPluginManager
    // Verify: the system-scope dependency artifact is present in the results
}
```

### Common pitfalls to avoid:

- ❌ **Testing only `compile` scope dependencies** — this misses the bug where system/provided scopes are dropped
- ❌ **Relying solely on dependency count assertions** — the count might match (e.g., 3 deps) but be missing the wrong ones
- ❌ **Calling the method without verifying all scope types** — the bug is that some scopes (like `system`) are silently excluded
- ❌ **Assuming the fix is about a different part of the code** — the root cause is that the scope-to-resolution mapping is incomplete, not a null check or exception handling issue

### Concrete example of what the buggy code does wrong:

In the buggy version, when the code maps dependency scopes to artifact resolution scopes, the mapping for `system` scope may be missing (e.g., a `Map` or `if-else` chain that handles `compile`, `runtime`, `test`, `provided` but omits `system`). This causes system-scope plugin dependencies to not be resolved, making them absent from the final resolved dependency list.

```java
// Buggy approach (scope mapping incomplete):
// if ("compile".equals(scope)) { return Artifact.SCOPE_COMPILE; }
// else if ("runtime".equals(scope)) { return Artifact.SCOPE_RUNTIME; }
// else if ("test".equals(scope)) { return Artifact.SCOPE_TEST; }
// else if ("provided".equals(scope)) { return Artifact.SCOPE_PROVIDED; }
// // Missing: system scope -> drops it silently!

// Fixed approach:
// if ("compile".equals(scope)) { return Artifact.SCOPE_COMPILE; }
// else if ("runtime".equals(scope)) { return Artifact.SCOPE_RUNTIME; }
// else if ("test".equals(scope)) { return Artifact.SCOPE_TEST; }
// else if ("provided".equals(scope)) { return Artifact.SCOPE_PROVIDED; }
// else if ("system".equals(scope)) { return Artifact.SCOPE_SYSTEM; } // <-- added
```

### What to assert in the test:

- Use `assertNotNull` or `assertTrue`/`assertThat` to check the system-scope artifact exists in the resolved dependencies
- Prefer checking by artifact ID or a unique property of the system-scope dependency
- If possible, assert the presence of **all** scope-type dependencies to future-proof the test