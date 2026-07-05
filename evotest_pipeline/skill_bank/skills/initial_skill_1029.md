---
name: filter-fulltext-property-restriction-leak
description: When a query Filter uses both full-text constraints (CONTAINS) and property
  restrictions (e.g., metadata path), a copy-on-write operation (FilterImpl#copy or
  constructor copy) must build a fresh property restrictions map; otherwise the copy
  shares state with the original, leaking old restrictions from the original into
  the copy's toString. Test by constructing a full-text filter, then forcing a copy/restrict,
  and verifying toString() does NOT contain property restrictions that were never
  set on the copy.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# filter-fulltext-property-restriction-leak

## Instructions

# Filter Full-Text Property Restriction Leak

## Instructions

- WHEN the TG encounters code that creates a copy-constructor or copy-from method for a Filter-like class that aggregates both a `fullTextConstraint` (FullTextExpression) and a `propertyRestrictions` map (Map&lt;String, PropertyRestriction&gt;):
  - THEN the TG should write a test that verifies that copying a Filter that has a full-text constraint but NO property restrictions produces a copy whose `toString()` representation does NOT include property restrictions from any previously copied source.
  - Specifically: construct a `FilterImpl` with only a full-text constraint (e.g., via `FilterTest.createFilter` + a `FullTextAndImpl` / `FullTextContainsImpl` wrapper), then call the copy method (e.g., the `FilterImpl(FilterImpl)` copy constructor, or `FilterImpl.copy()`) to produce a second filter, then set a property restriction on the *second* filter (e.g., via `restrictProperty`), and finally call `toString()` on the *first* (original) filter — assert that `first.toString()` does NOT contain the property restriction that was set on the second filter.
  - The bug manifests as: the copy constructor does `this.propertyRestrictions.putAll(impl.propertyRestrictions)`, sharing the same map reference, so subsequent mutation on the copy (e.g., `restrictProperty`) also mutates the original's map. The test must detect this by asserting that the original's state remains unchanged after mutating the copy.
  - Concrete string to assert: after setting a property restriction `"jcr:content/metadata/comment"` with `"is not null"` on the copy, the original's `toString()` should NOT contain `"property=[jcr:content/metadata/comment=[is not null]]"`.
  - Use full signatures: `org.apache.jackrabbit.oak.query.index.FilterImpl`, `org.apache.jackrabbit.oak.spi.query.FullTextExpression`, `org.apache.jackrabbit.oak.spi.query.FullTextAndImpl`.

- Common pitfalls to avoid:
  - Do NOT test only the copy for correctness while ignoring the original — the bug is that the original is mutated by side-effect.
  - Do NOT assume that just setting restrictions on different Filter objects is enough — the copy constructor must be exercised.
  - Do NOT rely on `getPropertyRestriction` returning null — the leak only appears in `toString()` if the shared map is mutated; use `toString()` to verify string representation.
  - Do NOT forget that `FullTextContainsImpl` must be wrapped in `FullTextAndImpl` (e.g., `new FullTextAndImpl(singletonList(contains))`) to be accepted by `setFullTextConstraint`.

- Example test pattern (pseudocode):
  ```java
  // Create a filter with a full-text constraint but no property restrictions
  FilterImpl original = createFilter(root, NodeTypeConstants.NT_BASE);
  FullTextExpression contains = new FullTextContainsImpl("december");
  original.setFullTextConstraint(new FullTextAndImpl(singletonList(contains)));

  // Copy the filter (this is where the bug may leak restrictions)
  FilterImpl copy = new FilterImpl(original);

  // Set a property restriction on the copy only
  copy.restrictProperty("jcr:content/metadata/comment", PropertyType.STRING, ...);

  // The original should NOT have the copy's property restriction
  assertFalse("Original filter must not contain copy's property restriction",
              original.toString().contains("property=[jcr:content/metadata/comment=[is not null]]"));
  ```

- Counter-example (incorrect test approach):
  ```java
  // BAD: only testing the copy, not verifying original's state
  FilterImpl copy = new FilterImpl(original);
  copy.restrictProperty(...);
  assertTrue(copy.getPropertyRestriction("comment") != null); // misses the mutation leak!
  ```