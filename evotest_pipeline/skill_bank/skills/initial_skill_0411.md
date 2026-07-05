---
name: path-input-sanitization
description: This skill teaches the TG to test path-like inputs that contain a trailing
  slash, a common edge case where path mapping/transform methods may incorrectly include
  or strip the trailing separator. Use this when testing path conversion, normalization,
  or mapping methods.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# path-input-sanitization

## Instructions

# Path Input Sanitization with Trailing Slash

## Instructions

- WHEN the TG encounters a method that transforms, maps, or converts a path string (e.g., `getOakPath(String jcrPath)`, `getJcrPath(String oakPath)`)
- THEN it should test with paths that have a **trailing slash** (`"/"`) at the end, including paths with and without namespace prefixes, and verify the output does NOT contain a trailing slash
- Common pitfalls:
  - Testing only "clean" paths without trailing slashes (e.g., testing only `"/foo:bar/quu:qux"` but not `"/foo:bar/quu:qux/"`)
  - Assuming the method will internally strip trailing slashes when it only does so via post-processing of parsed elements
  - Forgetting to test paths that go through the "simple path" fast-path (no namespace remapping) vs. the "full mapping" path
- Include at least the following:
  - A path with namespace prefixes and a trailing slash: `"/foo:bar/quu:qux/"` → expected `"/oak-foo:bar/oak-quu:qux"`
  - A simple path without namespace prefixes and a trailing slash: `"/a/b/c/"` → expected `"/a/b/c"` (no trailing slash)
  - The test should fail on the buggy version because the trailing slash is incorrectly preserved or the path is incorrectly handled
- The test pattern is **PARAMETRIC_TEST**: test with multiple path inputs each having a trailing slash, asserting the output equals the path without the trailing slash

### Correct Test Example

```java
@Test
public void testTrailingSlash() {
    assertEquals("/oak-foo:bar/oak-quu:qux", npMapper.getOakPath("/foo:bar/quu:qux/"));
    assertEquals("/a/b/c", npMapper.getOakPath("/a/b/c/"));
}
```

### Incorrect Test (Does Not Catch the Bug)

```java
@Test
public void testGetOakPath() {
    // Only tests clean paths without trailing slashes
    assertEquals("/oak-foo:bar/oak-quu:qux", npMapper.getOakPath("/foo:bar/quu:qux"));
    assertEquals("/a/b/c", npMapper.getOakPath("/a/b/c"));
}
```