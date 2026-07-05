---
name: type-filtered-default-toolchain-exclusion
description: When a method filters toolchains or similar objects by type AND adds
  default instances, test that default instances are only added for the matching type,
  not all registered types. The bug caused default toolchains from ALL factories to
  be appended even when only one specific type was requested.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- FILTERING_LOGIC
test_pattern: STATE_TEST
---

# type-filtered-default-toolchain-exclusion

## Instructions

# Type-Filtered Default Toolchain Exclusion

## Instructions

WHEN a method (like `DefaultToolchainManagerPrivate.getToolchainsForType(String type, MavenSession context)`) performs a type-filtered collection operation — where it:
1. Looks up a factory by type from a `Map<String, ToolchainFactory>` (e.g., `factories.get(type)`)
2. Uses that factory to create items matching the type from a configuration
3. Then iterates over ALL factories to add default items (e.g., `for (ToolchainFactory toolchainFactory : factories.values()) { toolchainFactory.createDefaultToolchain(); }`)

THEN the TG should write a state test that:
- Sets up TWO or more factories in the map, each for a different type (e.g., `"basic"` and `"rare"`)
- Calls the method with a specific type (e.g., `"basic"`)
- Verifies the result count is 1 (only the default for the matching type) — NOT 2 (defaults from ALL factories)
- On the buggy version, the result will be 2 because default toolchains from all registered factories are added indiscriminately
- On the fixed version, the result will be 1 because default toolchains are only added from the matching type's factory

Specifically:
- Use `HashMap<String, ToolchainFactory>` to inject mock factories
- Use `Mockito.when(factory.createDefaultToolchain()).thenReturn(mockToolchain)` on each factory
- Assert `assertEquals(1, result.length)` — the expected count is always exactly 1 default for the matched type (assuming no persisted toolchains)
- Assert that `logger.error()` was never called, confirming the type was found

Common pitfalls:
- Registering only ONE factory in the test setup makes this bug invisible — the bug only manifests when multiple factories are registered and the method incorrectly adds defaults from ALL of them
- Do NOT stub `createDefaultToolchain()` to return null for non-matching factories, as that would mask the bug; the bug is that the method calls the method at all on wrong factories
- Do NOT write the test as a mock interaction test verifying call counts — write it as a STATE test that checks the size of the returned array, because the bug manifests as extra elements in the result

Correct example:
```
@Test
public void testToolchainsForAvailableType() throws Exception {
    // Setup: register TWO mock factories
    ToolchainFactory factoryBasic = mock(ToolchainFactory.class);
    ToolchainFactory factoryRare = mock(ToolchainFactory.class);
    when(factoryBasic.createDefaultToolchain()).thenReturn(mock(ToolchainPrivate.class));
    when(factoryRare.createDefaultToolchain()).thenReturn(mock(ToolchainPrivate.class));
    
    Map<String, ToolchainFactory> factories = new HashMap<>();
    factories.put("basic", factoryBasic);
    factories.put("rare", factoryRare);
    toolchainManager.factories = factories;
    
    // Execute: request only "basic" type
    ToolchainPrivate[] result = toolchainManager.getToolchainsForType("basic", session);
    
    // Verify: only 1 default toolchain for "basic", NOT 2
    assertEquals(1, result.length);
}
```

Incorrect example (masks the bug):
```
@Test
public void testToolchainsForAvailableType() throws Exception {
    // Bug: only one factory registered — cannot detect the bug
    ToolchainFactory factoryBasic = mock(ToolchainFactory.class);
    when(factoryBasic.createDefaultToolchain()).thenReturn(mock(ToolchainPrivate.class));
    
    Map<String, ToolchainFactory> factories = new HashMap<>();
    factories.put("basic", factoryBasic);
    toolchainManager.factories = factories;
    
    ToolchainPrivate[] result = toolchainManager.getToolchainsForType("basic", session);
    assertEquals(1, result.length); // Would pass even on buggy version!
}
```