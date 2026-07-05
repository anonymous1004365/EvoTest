---
name: mounted-mapper-null-placeholder-request-resolution
description: WHEN a mount path contains optional placeholders (e.g., "${placeholder}")
  and a request URL provides fewer segments than the mount path even after accounting
  for defaults, THEN test that the mapper correctly returns null (unmounted) rather
  than incorrectly matching with a wrong page parameter count or returning zero entries.
  This skill applies to MountedMapper and similar URL routing mappers.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# mounted-mapper-null-placeholder-request-resolution

## Instructions

# Mounted Mapper Null Placeholder Request Resolution

## Instructions

WHEN the buggy code involves a MountedMapper (or AbstractBookmarkableMapper) that parses request URLs against a mount path containing optional placeholders (e.g., `/some/mount/${placeholder}/path`), and a request URL is shorter than the mount path but could be considered "compatible" by some logic:

- THEN test a request URL that has **exactly enough segments to reach the start of a placeholder section but not enough to complete it**, and verify that the mapper returns **null** (the request is not mapped) rather than returning an incorrect result.

- WHEN the mapper has logic like `if (urlCompatibility.matches(result))` or similar compatibility checks that could return a non-null result even when placeholder substitution cannot be satisfied, THEN verify that missing placeholder segments lead to a **null** return.

- WHEN the mount path contains segments like `some/mount/path` and the request URL is something like `some/mount` (fewer segments than even the fixed parts of the mount path before placeholders), THEN verify null is returned.

- WHEN the buggy code provides a `Map<String, String>` default parameter map and the mount path includes a `${placeholder}` that falls back to a default value, verify that when the request URL has fewer segments than the mount path (even accounting for placeholder defaults), the mapper correctly returns null.

- **Common pitfall**: Do NOT merely test with the same number of segments as the mount path has segments. Test with **fewer** segments where the deficit is in placeholder segments (e.g., mount path has 4 segments including a placeholder, request URL has 3 segments). The TG might only test with equal-length or excess-segment URLs and miss the underflow case.

- **Common pitfall**: Do NOT assume that because a placeholder has a default value, missing its segment in the URL is acceptable. Some implementations incorrectly return a match with the default value when they should return null because the mount pattern doesn't match.

**Example (correct test)**:
```java
@Test
void decode12()
{
    // mount path: "/some/mount/path" with optional placeholder "${placeholder}" 
    // e.g., mount path has 4 segments but placeholder has default
    // request: "/some/mount/path" — only 3 segments, missing the placeholder segment
    // Expected: null (unmounted), not a match
    PageParametersEncoder encoder = new PageParametersEncoder();
    MountedMapper mapper = new MountedMapper("/some/mount/${name}/path", MockPage.class, encoder);
    
    Request request = createRequest("/some/mount/path");
    Url url = Url.parse(request.getUrl());
    
    assertNull("When mount path has more segments than the request URL, " +
               "even with placeholder defaults, the mapper should return null",
               mapper.resolve(RequestMapper.MountInfo.fromRequest(request), url));
}
```

**Example (incorrect test)**:
```java
// WRONG: Only tests when segment count matches or exceeds
// mount path: "/some/mount/${name}/path"  (4 segments)
// request: "/some/mount/john/path"  (4 segments, matches)
Request request = createRequest("/some/mount/john/path");
assertNotNull(mapper.resolve(...)); // This is correct but insufficient

// WRONG: Missing the boundary case with fewer segments than mount path
// mount path: "/some/mount/${name}/path"  (4 segments)
// request: "/some/mount/path"  (3 segments — missing the placeholder segment)
// This case is where the bug manifests!
```

**Example (incorrect test #2 — wrong expected behavior)**:
```java
// WRONG: Assuming placeholder with default returns match for shorter URL
// mount path: "/segment1/${placeholder}/segment3" with default "defaultVal"
// request: "/segment1/segment3"  (2 segments instead of 3)
// The buggy code might incorrectly match this with placeholder=defaultVal
// Correctly, this should return null since the mount pattern doesn't match
Request request = createRequest("/segment1/segment3");
assertNotNull(mapper.resolve(...)); // WRONG — this should be assertNull for the bug
```