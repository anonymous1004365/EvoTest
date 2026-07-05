---
name: package-resource-minified-compression-flag
description: WHEN testing resource references that auto-detect whether a resource
  is already minified (name contains ".min."), THEN verify the compress flag is correctly
  set to false for already-minified resources and true for non-minified resources.
  This skill applies to PackageResourceReference, JavaScriptResourceReference, CssResourceReference,
  and their associated package resource classes that set compress flags based on the
  ".min." pattern in filenames.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# package-resource-minified-compression-flag

## Instructions

# Package Resource Minified Resource Compression Flag Detection

## Instructions

- WHEN the TG encounters a resource reference hierarchy where `CssPackageResource` or `JavaScriptPackageResource` constructors (or `PackageResourceReference.removeCompressFlagIfUnnecessary()`) use `name.contains(".min.")` to decide whether to set the `compress` flag (via `setCompress(false)` for already-minified resources)
- THEN the TG should write a test that:
  1. Creates a `CssResourceReference` or `JavaScriptResourceReference` pointing to a resource whose name contains `.min.` (e.g., `"b.min.js"` with scope `PackageResourceReferenceTest.class`)
  2. Calls `getResource()` on that reference to obtain the `CssPackageResource` or `JavaScriptPackageResource`
  3. Asserts that `resource.getCompress()` returns `false` (because the resource is already minified and must not be double-compressed)
  4. Also creates a reference pointing to a non-minified resource (e.g., `"a.js"` with the same scope) and asserts that its `getCompress()` returns `true`
  5. Enables minified resources via `Application.get().getResourceSettings().setUseMinifiedResources(true)` before the test assertions
- Common pitfalls to avoid:
  - Testing **only** the `getMinifiedName()` method (e.g., `html5.min.js` → `html5.min.js`) without checking the **compress flag** on the actual resource object. The bug is about whether `getResource()` returns a resource with `compress=false` for already-minified names — the minified name detection may work fine while the compress flag is still wrong.
  - Testing only one resource type (e.g., only `JavaScriptResourceReference`) when the same pattern exists in both `CssPackageResource` and `JavaScriptPackageResource` constructors and in `PackageResourceReference.removeCompressFlagIfUnnecessary()`.
  - Forgetting to call `setUseMinifiedResources(true)` so that the detection logic is triggered.
  - Asserting `assertTrue(alreadyMinifiedResource.getCompress())` (expecting true) instead of `assertFalse()` on a `.min.js` resource.

- **Correct example:**
  ```java
  @Test
  public void testMinifiedResourcesDetection()
  {
      Application.get().getResourceSettings().setUseMinifiedResources(true);
      
      // Non-minified resource should be compressible
      JavaScriptResourceReference notMinified = 
          new JavaScriptResourceReference(MyClass.class, "a.js");
      JavaScriptPackageResource notMinifiedResource = notMinified.getResource();
      assertTrue("Not minified resource should have compress=true", 
          notMinifiedResource.getCompress());
      
      // Already-minified resource should NOT be compressed again
      JavaScriptResourceReference alreadyMinified = 
          new JavaScriptResourceReference(MyClass.class, "b.min.js");
      JavaScriptPackageResource alreadyMinifiedResource = alreadyMinified.getResource();
      assertFalse("Already minified resource should have compress=false", 
          alreadyMinifiedResource.getCompress());
  }
  ```

- **Incorrect example (pitfall):**
  ```java
  // Tests only getMinifiedName(), not the compress flag!
  PackageResourceReference ref = new PackageResourceReference("b.min.js");
  assertEquals("b.min.js", ref.getMinifiedName());  // This passes even if the bug exists
  ```