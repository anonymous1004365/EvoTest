---
name: minified-name-false-positive-detection
description: ''
code_tags:
- STRING_PARSING
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# minified-name-false-positive-detection

## Instructions

# Minified Name False Positive Detection

## Instructions

- WHEN the TG encounters a method that computes a "minified name" for a resource by appending a minification postfix (e.g., `ResourceUtils.getMinifiedName(name, "min")`), and the input resource name already contains the dot-separated min postfix as a substring (e.g., `html5.min.js` where `.min.` appears before the final extension)
- THEN the TG should create a parametric test that:
    1. Calls `getMinifiedName()` with resource names where the term "min" appears in different positions (as a legitimate part of the name like `html5.min.js`, `something.notmin.js`, `justamin.js`, `html5.min`)
    2. Verifies that when the name already ends with the `.min.EXT` pattern (e.g., `html5.min.js`), the method returns the same name unchanged, NOT `html5.min.min.js`
    3. Uses `Assert.assertEquals(expected, actual)` to compare against the correct expected minified name
    4. Tests both names WITH a file extension and WITHOUT an extension (e.g., `html5.min` should remain `html5.min`, not become `html5.min.min`)

- Common pitfalls to avoid:
    - Testing only the normal case where the name does NOT contain "min" — the bug occurs specifically with names like `html5.min.js` where `.min` appears before `.js`
    - Assuming the algorithm correctly detects already-minified names by checking if the extension is `.min` or the basename ends with `.min.` — the bug was that `html5.min.js` was incorrectly transformed to `html5.min.min.js` because the condition `!baseName.endsWith(dottedPostfix + ".")` was not being evaluated correctly for this case
    - Not testing names without extensions like `html5.min` — the test should cover edge cases at the boundary where "min" appears as the last segment before a dot or without any extension

### Example (Correct Test)

```java
@Test
public void testGetMinifiedName_CorrectBehavior()
{
    // Name already ends with .min.EXT — should NOT add another .min
    Assert.assertEquals("html5.min.js", 
        ResourceUtils.getMinifiedName("html5.min.js", ResourceUtils.MIN_POSTFIX_DEFAULT));

    // Normal case — should add .min before extension
    Assert.assertEquals("html5.notmin.min.js", 
        ResourceUtils.getMinifiedName("html5.notmin.js", ResourceUtils.MIN_POSTFIX_DEFAULT));

    // No extension — should append .min
    Assert.assertEquals("html5notmin.min", 
        ResourceUtils.getMinifiedName("html5notmin", ResourceUtils.MIN_POSTFIX_DEFAULT));

    // Already minified, no extension — should remain unchanged
    Assert.assertEquals("html5.min", 
        ResourceUtils.getMinifiedName("html5.min", ResourceUtils.MIN_POSTFIX_DEFAULT));
}
```

### Example (Incorrect Test — Missing the Bug)

```java
// ❌ WRONG — only tests the normal case, misses the false positive
@Test
public void testGetMinifiedName()
{
    Assert.assertEquals("mystyle.min.css", 
        ResourceUtils.getMinifiedName("mystyle.css", ResourceUtils.MIN_POSTFIX_DEFAULT));
    // Missing: html5.min.js → should stay html5.min.js, not become html5.min.min.js
}
```