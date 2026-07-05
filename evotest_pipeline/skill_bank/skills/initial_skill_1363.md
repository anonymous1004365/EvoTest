---
name: mandatory-placeholder-parameter-validation
description: When testing URL mappers with placeholder parameters in mount paths,
  some placeholders may be required ($) or optional (#). Test that buildUrl() returns
  null when a required placeholder parameter is missing from PageParameters, and test
  that it succeeds with optional parameters missing. Do not assume all placeholders
  are optional or test only String values.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# mandatory-placeholder-parameter-validation

## Instructions

# Mandatory Placeholder Parameter Validation

## Instructions

WHEN the TG encounters a URL mapper (e.g. `MountedMapper`, `PackageMapper`, or any subclass of `AbstractBookmarkableMapper`) whose mount path contains placeholder parameters (syntax `${paramName}` or `#{paramName}`):

- THEN the TG must identify which parameters are **required** (`${...}` syntax) vs **optional** (`#{...}` syntax) by examining the mount path string.
- THEN the TG must write a test that verifies that `mapHandler(...)` (or equivalently `buildUrl(...)`) returns `null` when a **required** placeholder parameter is missing from the `PageParameters`.
- For example, with mount path `/some/${param1}/path/${param2}`, verify that both `param1` and `param2` are mandatory:
  - Providing only one of them must result in `null` from `mapHandler()`.
  - Providing no placeholder parameters must also result in `null`.
- THEN the TG must also verify that **optional** parameters (`#{...}` syntax) can be omitted without causing `null` to be returned.
- THEN the TG must use a concrete `IRequestHandler` that carries the parameters, e.g. `BookmarkablePageRequestHandler` or a `RenderPageRequestHandler` built with an `IPageProvider` that has `PageParameters`.

### Common pitfalls to avoid:
- ❌ Testing only with `String` values for placeholders — parameters can be other types too, but the mapper cares about whether the named key exists, not its value type.
- ❌ Assuming `mapHandler()` will always return a non-null `Url` even when required placeholders are missing.
- ❌ Only testing the decode (parsing) direction but not the encode (URL building) direction.
- ❌ Using a plain `MountedMapper` without overriding `getContext()` — you must provide a proper `IMapperContext` instance (e.g. using an anonymous subclass).

### Correct example:
```java
// MountedMapper with two required placeholder parameters
private final MountedMapper placeholderEncoder = new MountedMapper(
    "/some/${param1}/path/${param2}", MockPage.class)
{
    @Override
    protected IMapperContext getContext()
    {
        return context;
    }

    @Override
    boolean getRecreateMountedPagesAfterExpiry()
    {
        return true;
    }
};

@Test
public void placeholderEncode_requiredMissing_returnsNull()
{
    // Test: param1 provided but param2 missing -> should return null
    PageParameters params = new PageParameters();
    params.set("param1", "value1");
    // param2 is NOT set -> mandatory parameter missing
    IRequestHandler handler = new BookmarkablePageRequestHandler(
        new PageProvider(MockPage.class, params));
    
    Url url = placeholderEncoder.mapHandler(handler);
    
    assertNull("Expected null when required placeholder parameter 'param2' is missing", url);
}

@Test
public void placeholderEncode_bothRequiredProvided_succeeds()
{
    // Test: both required parameters provided -> should succeed
    PageParameters params = new PageParameters();
    params.set("param1", "value1");
    params.set("param2", "value2");
    IRequestHandler handler = new BookmarkablePageRequestHandler(
        new PageProvider(MockPage.class, params));
    
    Url url = placeholderEncoder.mapHandler(handler);
    
    assertNotNull(url);
    assertEquals("/some/value1/path/value2", url.toString());
}
```

### Incorrect example (pitfall):
```java
// ❌ WRONG: Only testing with one parameter and not verifying that all required params are needed
@Test
public void placeholderEncode_wrong()
{
    PageParameters params = new PageParameters();
    params.set("param1", "test");
    // missing param2 but expecting success — WRONG
    IRequestHandler handler = new BookmarkablePageRequestHandler(
        new PageProvider(MockPage.class, params));
    
    Url url = placeholderEncoder.mapHandler(handler);
    assertNotNull(url); // ❌ This will fail on the fixed version but the test doesn't catch it
}
```