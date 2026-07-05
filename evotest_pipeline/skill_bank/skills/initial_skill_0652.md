---
name: compatibilty-score-request-mapper
description: ''
code_tags:
- VALIDATION
- COMPATIBILITY_SCORE
test_pattern: INTERACTION_TEST
---

# compatibilty-score-request-mapper

## Instructions

# Compatibility Score for Request Mappers

## Instructions

WHEN the TG encounters a class that extends `AbstractBookmarkableMapper` (or similar mapper base class) and overrides `getCompatibilityScore(Request request)`:

- THEN the TG should test that the method returns a positive score (equal to `mountSegments.length`) when the request URL starts with the mount path segments, using `urlStartsWith(request.getUrl(), mountSegments)`.
- THEN the TG should test that the method returns `0` when the request URL does NOT start with the mount path segments.
- THEN the TG should construct a `Request` with a URL whose segments start with the same mount path used to construct the mapper (e.g., `Url.parse("mount/path/MockPage")` for a mapper mounted at `"mount/path"`).
- THEN the TG should verify the returned integer score is > 0 (specifically equal to `mountSegments.length`, e.g., `2` for a 2-segment mount path like `"mount/path"`).
- Common pitfalls to avoid:
  - Do NOT write `getCompatibilityScore` returning a constant `0` — this defeats the mapper priority system entirely.
  - Do NOT forget to call `urlStartsWith(request.getUrl(), mountSegments)` inside the method implementation — that is the standard pattern for checking whether the request URL matches the mapper's mount path.
  - Do NOT test only the conditions where the request matches; also test the negative case (a request to an unrelated URL path).

### Correct Example (what the fixed code should look like)

```java
@Override
public int getCompatibilityScore(Request request)
{
    if (urlStartsWith(request.getUrl(), mountSegments))
    {
        return mountSegments.length;
    }
    else
    {
        return 0;
    }
}
```

### Incorrect Example (the bug)

```java
@Override
public int getCompatibilityScore(Request request)
{
    // always returns 0 — this mapper will never win against other mappers
    return 0;
}
```

### Test Example (what the triggering test should verify)

```java
@Test
public void testGetCompatibilityScore()
{
    PackageMapper mapper = new PackageMapper("mount/path", PackageName.forClass(MockPage.class))
    {
        @Override
        protected IMapperContext getContext()
        {
            return context;
        }
    };

    // A request whose URL starts with the mount path
    Request matchingRequest = getRequest(Url.parse("mount/path/MockPage"));
    int score = mapper.getCompatibilityScore(matchingRequest);
    assertEquals(2, score); // mountSegments.length = 2 for "mount/path"

    // A request whose URL does NOT start with the mount path
    Request nonMatchingRequest = getRequest(Url.parse("other/Page"));
    score = mapper.getCompatibilityScore(nonMatchingRequest);
    assertEquals(0, score);
}
```