---
name: overlapping-tablet-boundary-row-handling
description: Teaches how to test methods that find overlapping tablets for bulk import,
  especially when boundary rows involve null/infinite end rows. Use when a method
  processes KeyExtent objects to determine which tablets a file overlaps.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- COLLECTION_OPERATIONS
test_pattern: PARAMETRIC_TEST
---

# overlapping-tablet-boundary-row-handling

## Instructions

# Overlapping Tablet Boundary Row Handling

## Instructions

- WHEN the TG encounters a method like `findOverlappingTablets` that locates tablets overlapping a file or a `KeyExtent` with potentially null or infinite start/end rows (e.g., `Text("h")` as end row, or `null` as start row representing negative infinity)
- THEN the TG MUST write tests that exercise every branch dealing with:
  1. **Null start row / null end row** on `KeyExtent` — these represent infinite bounds ("-inf" to some row, or some row to "+inf"). The method must handle them without throwing NPE.
  2. **Empty byte array vs. null** for start/end row — they are semantically different. A `Text("")` is NOT the same as `null`. The method should treat `null` as no bound (infinite), not as a zero-length bound.
  3. **Comparison of boundary rows** — when comparing a file's start row against a tablet's end row (or vice versa), the code must correctly handle `null` on either side. Testing with `null` vs. non-null is critical.
  4. **Result list size** — the test MUST assert the exact number of overlapping tablets returned (e.g., `assertEquals(5, overlaps.size())`). An off-by-one bug causes exactly one missing tablet.

- Key pitfalls to avoid:
  - ❌ Testing only non-null start/end rows — this misses the null-boundary bug.
  - ❌ Testing only the happy path where a file maps to one tablet — real bulk import files often span multiple tablets.
  - ❌ Assuming that `getStartRowForExtent` returns `null` for the first tablet — verify this explicitly.
  - ❌ Not testing that the list includes the tablet at the boundary (e.g., the tablet whose start row equals the file's start row).

- Correct test approach:
```java
// Test a file whose start row falls exactly at a tablet boundary
// The file spans multiple tablets, including one with null start row (first tablet)
KeyExtent extent = new KeyExtent(tableId, new Text("h"), new Text("1\0"));
List<TabletLocation> overlaps = BulkImporter.findOverlappingTablets(context, vm, locator, new Path(file));
// Should include the tablet covering null → "1\0" (first tablet) AND tablets up to "h"
assertEquals(5, overlaps.size());

// Also test getStartRowForExtent returns null for the first tablet
assertEquals(null, BulkImporter.getStartRowForExtent(extent)); // first tablet has null start
```

- Incorrect test approach (what you want to avoid):
```java
// ❌ Only testing a file that maps to a single tablet
// ❌ Not asserting the size or testing null boundaries
KeyExtent extent = new KeyExtent(tableId, new Text("h"), new Text("g"));
List<TabletLocation> overlaps = BulkImporter.findOverlappingTablets(context, vm, locator, new Path(file));
// Without null-boundary test, the off-by-one bug is not caught
```

- **When to apply this skill**: Every time a method uses `KeyExtent` with potentially null rows, or compares `Text` objects where either side may be `null`. This commonly occurs in Accumulo's tablet location logic, bulk import, and split/merge operations.