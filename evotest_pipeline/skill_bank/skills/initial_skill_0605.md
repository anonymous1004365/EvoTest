---
name: lucene-index-dir-wrapping-order
description: When configuring a Lucene index with a Directory wrapper (e.g., copy-on-read),
  the `:indexPath` property must be set BEFORE wrapping the directory. Tests that
  modify index definitions and assert on the resulting NodeState should verify that
  the `:indexPath` property is present even when the index definition includes a directory
  wrapper configuration, and catch cases where directory wrapping is done before the
  index path is set.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# lucene-index-dir-wrapping-order

## Instructions

# Lucene Index Directory Wrapping Order

## Instructions

When testing a Lucene index that uses a directory wrapper (e.g., `CopyOnReadDirectory`, `IndexCopier`, or any `Directory` wrapping configured via `dir` provider options):

- WHEN the test configures an index definition that includes both:
  1. A `dir` provider option (e.g., `dir`, `dir@CopyOnRead`) that triggers directory wrapping
  2. An `:indexPath` property (or expects it to be automatically set)
- THEN the test MUST verify that the resulting index node state contains the `:indexPath` property.
- Use `assertTrue(nodeState.hasProperty(":indexPath"))` or assert the property is not null.
- The test should trigger the index commit/merge operation that processes the index definition and produces the final node state.
- Common pitfall: Testing only that the index is usable (e.g., queries return results) without checking that `:indexPath` metadata is persisted. The bug occurs when directory wrapping happens *before* the index path is set, leaving the property missing. A test that only checks query results may pass even with this bug if the index still works functionally.
- The triggering test method should specifically test a "compat" scenario (compatibility mode with the directory wrapper) and verify the `:indexPath` property is present on the final node state.

### Example (Correct — would catch the bug):
```java
// After configuring index definition with dir provider
// and running the index commit/merge
NodeState after = ...; // the resulting node state after indexing
assertTrue(":indexPath property must be present", after.hasProperty(":indexPath"));
```

### Example (Incorrect — would NOT catch the bug):
```java
// Only checking that search works
List<String> result = executeQuery("SELECT * FROM [nt:base] WHERE ...");
assertFalse("Should return results", result.isEmpty());
// Missing assertion on :indexPath property
```