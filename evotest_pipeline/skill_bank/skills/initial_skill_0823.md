---
name: extra-config-loading-validation
description: When adding extra configuration sources during local config creation,
  test that proxy template parameters handle type-mismatch scenarios like String vs
  CtTypeReference. This skill helps prevent ClassCastException or incorrect config
  loading.
code_tags:
- VARIABLE_RESOLUTION
test_pattern: EXCEPTION_TEST
---

# extra-config-loading-validation

## Instructions

# Extra Config Loading Validation

## Instructions

WHEN the TG encounters code that creates or loads local configuration (e.g., a `ConfigUtil.createLocalConfig` method) and passes extra configuration sources (e.g., a `List<ConfigSource>` or similar collection of dynamic proxy-based template parameters), THEN the TG should:

1. **Test with type-mismatched extra configuration**: Write a test that passes extra configuration values that do not match the expected proxy interface type (e.g., passing a `String` where a `CtTypeReference` or specialized proxy type is expected). Verify that the system handles it gracefully — either by skipping the mismatched entry or by throwing a meaningful exception rather than a `ClassCastException`.

2. **Test with null or empty extra configuration**: Pass `null` or an empty list for the extra configuration sources and verify the method completes without throwing an unexpected `NullPointerException`.

3. **Test with boundary values**: Include a test case where the extra configuration contains a valid but edge-case value (e.g., a proxy parameter that references a non-existent template variable) to ensure proper validation or error reporting.

4. **Expect specific exceptions on buggy version**: The buggy code may throw a `ClassCastException` when a proxy template parameter of type `String` is incorrectly cast to a `CtTypeReference` or other specialized type. Write the test to verify that the fixed version either skips such mismatches or throws a more informative exception (e.g., `IllegalArgumentException`).

5. **Avoid these common pitfalls**:
   - Testing only with valid/strictly-typed extra configuration entries, which would not expose the proxy template type-mismatch bug.
   - Assuming all proxy parameters conform to a single interface type without considering that template variable references may be plain `String` objects.
   - Neglecting to test the case where extra configuration is completely absent or empty, which may reveal a different null-safety issue on the buggy version.

### Correct test example (fixed version behavior):
```java
@Test
public void testCreateLocalConfigWithExtraConfig_stringTypeParam() {
    // This test verifies that passing a String-based extra config
    // does not cause a ClassCastException when proxy template parameters
    // expect a CtTypeReference
    List<ConfigSource> extraConfigs = new ArrayList<>();
    extraConfigs.add(new StringConfigSource("proxy.param", "someValue"));
    assertDoesNotThrow(() -> ConfigUtil.createLocalConfig(extraConfigs));
}
```

### Incorrect test example (missing the mismatch):
```java
@Test
public void testCreateLocalConfigWithExtraConfig() {
    // BAD: Only tests with typed proxy parameters, missing the String case
    List<ConfigSource> extraConfigs = new ArrayList<>();
    extraConfigs.add(new CtTypeReferenceConfigSource("proxy.param", someCtTypeRef));
    ConfigUtil.createLocalConfig(extraConfigs); // passes fine but misses the bug
}
```