---
name: template-parameter-type-validation
description: When an iterator initializes with term sources and seeks on column families, validate that each TermSource's seekColfams is correctly set to the user-configured column family. Tests should verify that IndexedDocIterator uses the configured indexFamily option instead of default term-based column families.
code_tags: ['VALIDATION', 'STATE_MUTATION', 'ORDER_DEPENDENCY']
test_pattern: STATE_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters an iterator that extends IntersectingIterator (e.g., IndexedDocIterator, FamilyIntersectingIterator) and overrides `init()` to configure column families via options
- THEN it should test that after initialization with a custom `indexFamily` option (e.g., `"indexFamily" -> "i"`), the TermSource objects in `sources` each have their `seekColfams` set to a `Set<ByteSequence>` containing an `ArrayByteSequence` wrapping that custom column family name, rather than the TermSource's own term-based column family
- The test should verify that the iterator ignores any column families passed to `seek(Range, Collection, boolean)` and instead uses the column families configured in `TermSource.seekColfams` during `init()`
- Common pitfalls:
  - Testing only with default column families (e.g., `DEFAULT_INDEX_COLF`) and missing the custom configuration path
  - Forgetting that `TermSource` constructor sets `seekColfams` from its `term` parameter, and that `IndexedDocIterator.init()` overrides this with `indexColfSet`
  - Not checking that ALL TermSource entries have been updated, not just the first one
  - Expecting `seek(Range, Collection, boolean)` to respect the passed `seekColumnFamilies` instead of the internally configured ones

### Example

Correct test approach:
```java
// Configure IndexedDocIterator with a custom indexFamily
IteratorSetting is = new IteratorSetting(1, IndexedDocIterator.class);
IndexedDocIterator.setColumnFamilies(is, new Text[] {new Text("term1"), new Text("term2")});
is.addOption("indexFamily", "customIndexFamily");

IndexedDocIterator iter = new IndexedDocIterator();
SortedKeyValueIterator<Key,Value> source = createIteratorStack(...);
iter.init(source, is.getOptions(), env);

// Verify each TermSource.seekColfams uses the configured indexFamily, not the term
for (TermSource ts : iter.sources) {
    ByteSequence expectedColFam = new ArrayByteSequence("customIndexFamily".getBytes());
    assertTrue("seekColfams should contain the configured indexFamily",
        ts.seekColfams.contains(expectedColFam));
    assertEquals(1, ts.seekColfams.size());
}
```

Incorrect test approach:
```java
// WRONG: Only testing with default indexFamily
IteratorSetting is = new IteratorSetting(1, IndexedDocIterator.class);
IndexedDocIterator.setColumnFamilies(is, new Text[] {new Text("term1")});
// Missing explicit "indexFamily" option - defaults to "i"
IndexedDocIterator iter = new IndexedDocIterator();
iter.init(source, is.getOptions(), env);

// This passes even if the bug exists, because default "i" happens to match
for (TermSource ts : iter.sources) {
    assertEquals(1, ts.seekColfams.size());
    // Doesn't verify what the content is
}
```