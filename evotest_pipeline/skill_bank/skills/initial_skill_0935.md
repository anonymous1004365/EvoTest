---
name: anonymous-enum-resource-key-generation
description: When testing resource key generation for enum choice renderers that use
  Classes.simpleName(), test with anonymous enum constants where getDeclaringClass()
  returns the parent enum class. The bug causes incorrect key because getSimpleName()
  on anonymous enum constants returns empty string instead of the parent enum class
  simple name.
code_tags:
- COMPARATOR_IMPLEMENTATION
- ANONYMOUS_ENUM_RESOURCE_KEY
- TYPE_CONVERSION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# anonymous-enum-resource-key-generation

## Instructions

# Anonymous Enum Resource Key Generation

## Instructions

**WHEN** the TG encounters `EnumChoiceRenderer` or similar classes that generate resource keys using `Classes.simpleName(object.getDeclaringClass())` or `object.getDeclaringClass().getSimpleName()` for enum values:

**THEN** the TG should test with anonymous enum constants (enum values that have a body, e.g. `ANONYMOUS { }`), because:
- For anonymous enum constants, `getDeclaringClass()` correctly returns the parent enum class
- But `getSimpleName()` on an anonymous class returns an empty string (`""`) instead of the parent enum's simple name
- The class `org.apache.wicket.util.lang.Classes` has a helper method `simpleName(Class<?> c)` that resolves anonymous classes by walking up the superclass chain — use it instead of `Class.getSimpleName()`
- The expected resource key format is `<EnumSimpleName>.<enumConstantName>`, e.g., `TestEnum.ANONYMOUS`

**WHEN** the TG tests resource key generation:

**THEN** the TG should:
1. Define a test enum with at least one anonymous constant (e.g., `ANONYMOUS { }`)
2. Create an `EnumChoiceRenderer` instance: `new EnumChoiceRenderer<TestEnum>()`
3. Call `renderer.resourceKey(TestEnum.ANONYMOUS)` and assert it equals `"TestEnum.ANONYMOUS"`
4. Also test with a non-anonymous constant (e.g., `REGULAR`) to verify both cases work
5. If the code uses `Classes.simpleName()` (Wicket's helper), verify it handles anonymous enums correctly; if it uses bare `Class.getSimpleName()`, the test should expect a bug.

**Common pitfalls:**
- ❌ Testing only with regular (non-anonymous) enum constants — these pass even with the bug
- ❌ Assuming `getDeclaringClass().getSimpleName()` returns the same as `getSimpleName()` — they differ for anonymous enum values
- ❌ Using `object.getClass().getSimpleName()` instead of `object.getDeclaringClass()` — both fail for anonymous enums but in different ways
- ❌ Not including an anonymous enum constant in the test at all

**Example correct test:**

```java
public enum TestEnum {
    REGULAR,
    ANONYMOUS {
        // anonymous enum value with body
    }
}

@Test
public void testResourceKeyGenerationForAnonymousEnums() {
    EnumChoiceRenderer<TestEnum> renderer = new EnumChoiceRenderer<TestEnum>();
    
    // Non-anonymous: works even with buggy code
    assertEquals("TestEnum.REGULAR", renderer.resourceKey(TestEnum.REGULAR));
    
    // Anonymous: breaks if using bare getSimpleName() instead of Classes.simpleName()
    assertEquals("TestEnum.ANONYMOUS", renderer.resourceKey(TestEnum.ANONYMOUS));
}
```

**Example incorrect test (would miss the bug):**

```java
@Test
public void testResourceKeyGeneration() {
    // BUG: Only tests non-anonymous enum constants
    EnumChoiceRenderer<TestEnum> renderer = new EnumChoiceRenderer<TestEnum>();
    assertEquals("TestEnum.REGULAR", renderer.resourceKey(TestEnum.REGULAR));
    // Missing anonymous enum test case!
}
```