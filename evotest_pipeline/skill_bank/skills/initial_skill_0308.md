---
name: minified-name-detection-no-duplicate-suffix
description: When detecting or adding a minified file suffix (like '.min.js'), the
  TG should test that a filename already containing the minified marker (e.g., 'html5.min.js')
  is not incorrectly altered to have the suffix appended again (e.g., becoming 'html5.min.min.js').
code_tags:
- VALIDATION
- STRING_PROCESSING
test_pattern: STATE_TEST
---

# minified-name-detection-no-duplicate-suffix

## Instructions

# Minified Name Detection Should Not Duplicate the Suffix

## Instructions

- WHEN the TG sees code that computes a "minified" version of a filename by detecting whether a minified marker (e.g., `min`) already exists as part of the filename AND appends a suffix pattern like `.{minMarker}.{extension}`
- THEN the TG should test with filenames where the **final filename segment before the extension already contains the minified marker** (e.g., `html5.min.js`, `library.min.css`, `script.min.debug.js`), and verify that the computed minified name equals the original filename itself (no duplicate suffix appended)
  - For example: `getMinifiedName()` on a `PackageResourceReference` pointing to `html5.min.js` should return `"html5.min.js"`, NOT `"html5.min.min.js"`
- Include test cases where the minified marker (`min`) appears:
  1. As the final stem before the extension: `html5.min.js` → expected: `html5.min.js`
  2. As a substring in the final stem: `html5notmin.min` → expected: `html5notmin.min`
  3. Without extension: `html5notmin.min` → expected: `html5notmin.min`
- Verify the output using assertions like `Assert.assertEquals(expectedMinifiedName, resource.getMinifiedName())`
- **Common pitfall**: Testing only filenames that do NOT already contain the minified marker (e.g., `script.js` → `script.min.js`), which passes even if the bug is present. Always also test filenames that DO contain the marker in their base name to catch duplicate-suffix bugs.

### Correct example (catches the bug):
```java
// The bug: "html5.min.js" → getMinifiedName() incorrectly returns "html5.min.min.js"
PackageResourceReference html5minjs = new PackageResourceReference(
    PackageResourceReferenceTest.class, "html5.min.js");
Assert.assertEquals("html5.min.js", html5minjs.getMinifiedName());

// Also test edge cases
PackageResourceReference html5notminjs = new PackageResourceReference(
    PackageResourceReferenceTest.class, "html5.notmin.min.js");
Assert.assertEquals("html5.notmin.min.js", html5notminjs.getMinifiedName());

PackageResourceReference html5notmin = new PackageResourceReference(
    PackageResourceReferenceTest.class, "html5notmin.min");
Assert.assertEquals("html5notmin.min", html5notmin.getMinifiedName());
```

### Incorrect example (misses the bug):
```java
// Only tests filenames without the min marker in the name — passes even with the bug
PackageResourceReference script = new PackageResourceReference(
    PackageResourceReferenceTest.class, "script.js");
Assert.assertEquals("script.min.js", script.getMinifiedName());
// This test alone does NOT catch the duplicate-suffix bug!
```