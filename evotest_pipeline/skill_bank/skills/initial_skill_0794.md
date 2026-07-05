---
name: location-tracker-exclusion-from-interpolation
description: When an interpolator traverses an object model and visits user-facing
  properties, it must skip internal tracking/audit fields that hold mutable state
  references. Test that LocationTracker fields are NOT interpolated and that their
  values remain unchanged after model interpolation.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# location-tracker-exclusion-from-interpolation

## Instructions

# LocationTracker Fields Must Be Excluded From Model Interpolation

## Instructions

- WHEN the interpolator processes an object model (e.g., a Maven Model, ModelBase, InputLocationTracker) that contains fields storing **mutable internal tracking objects** (such as `InputLocation` or `LocationTracker` instances)
- THEN the TG should verify that these **internal-tracking fields** are **excluded from interpolation** — their values must remain **unchanged** after `interpolateModel()` or any similar full-model interpolation method is called
- This applies specifically to fields that are **not user-settable POM properties** but rather **framework-managed state** used for tracking file source locations, line numbers, or column positions (any class implementing `InputLocationTracker`)
- The test should:
  1. **Set up an object model** (e.g., `Model`) that contains `LocationTracker` / `InputLocation` data on its fields
  2. **Capture the initial values** of these location-tracking fields (after construction but before interpolation)
  3. **Call the interpolator** on the model object (or a parent model containing it) — the same method that interpolates `${...}` placeholders in POM properties
  4. **Assert that the LocationTracker fields remain identical** to their original values (e.g., assertSame or assertEquals on the InputLocation reference / value)
- **Expect the test to FAIL on the buggy version** because the buggy interpolator overwrites/modifies LocationTracker data during interpolation, corrupting the source-location information
- **Common pitfalls to avoid:**
  - ❌ Testing only String-typed POM properties (like `model.getVersion()`) — the bug is specific to **non-property tracking fields**, not user-facing strings
  - ❌ Forgetting to call the specific interpolation method the production code uses (e.g., `interpolateModel()` or `interpolateObject()` with `ModelBuildingRequest`)
  - ❌ Asserting on the wrong granularity — you must assert **before-and-after identity/reference equality** for the specific LocationTracker field(s), not just that the model is non-null
  - ❌ Assuming interpolation is a no-op — the correct behavior is that location-tracking data is excluded; the test must verify this exclusion explicitly

### Correct Example (what the test should do)
```java
// Arrange
Model model = new Model();
// ... set up model with location tracking data ...
InputLocation originalLocation = model.getLocation("groupId");
assertNotNull("test requires pre-set location", originalLocation);

// Act
ModelInterpolator interpolator = new StringSearchModelInterpolator();
interpolator.interpolateModel(model, projectDir, request, problems);

// Assert
InputLocation interpolatedLocation = model.getLocation("groupId");
assertSame(
    "LocationTracker data must NOT be modified by interpolation",
    originalLocation, interpolatedLocation
);
```

### Incorrect Example (what the test should NOT do)
```java
// ❌ Only testing user-facing String fields — misses the bug entirely
Model model = new Model();
model.setVersion("${project.version}");
interpolator.interpolateModel(model, ...);
assertEquals("resolved", model.getVersion());

// ❌ Not verifying identity — just checking non-null
assertNotNull(model.getLocation("groupId")); // won't catch corruption
```