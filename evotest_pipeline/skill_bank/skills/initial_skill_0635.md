---
name: mounted-mapper-enum-parameter-handling
description: Tests when MountedMapper encodes paths with page class parameters that
  are enum types, the mapper must correctly handle both String parameters (from the
  URL) and CtTypeReference parameters (for enum classes). The test should verify that
  encoding does not throw ClassCastException and produces correct mount paths.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# mounted-mapper-enum-parameter-handling

## Instructions

# MountedMapper Enum Parameter Encoding

## Instructions

- WHEN the TG encounters `MountedMapper` encoding a request that uses a page class whose constructor takes parameters that include an enum type
- THEN the TG must test that `MountedMapper.encode()` correctly handles both:
  1. A `String` parameter value (as would come from URL parsing) — e.g. `"SOME_VALUE"`
  2. A `CtTypeReference` parameter value (as would come from the mount path definition for the enum class)
- The TG should verify that calling `mapper.encode()` with a `PageParameters` containing a mix of `String` and non-`String` values does NOT throw a `ClassCastException` and returns the correct mounted URL path

- Common pitfalls:
  - Testing only with `String` parameter values and missing the scenario where parameters are objects like `CtTypeReference`
  - Assuming `mapper.encode()` handles all parameter types uniformly without testing type coercion
  - Not verifying that the encoded URL path matches the expected pattern for mounted pages with enum parameters

## Examples

Correct test approach:
```java
// Test that encoding works with both String and CtTypeReference parameter values
MountedMapper mapper = new MountedMapper("/path", MyPage.class);
PageParameters params = new PageParameters();
params.set("enumParam", "SOME_VALUE");
params.set("typeParam", new CtTypeReference<MyEnum>() {});
IRequestHandler handler = new ListenerRequestHandler(page, ...);
Url url = mapper.encode(handler);
// Verify no ClassCastException and correct URL
```

Incorrect test approach:
```java
// Only testing with String values — misses the bug
MountedMapper mapper = new MountedMapper("/path", MyPage.class);
PageParameters params = new PageParameters();
params.set("enumParam", "SOME_VALUE");  // only String values tested
Url url = mapper.encode(handler);
```