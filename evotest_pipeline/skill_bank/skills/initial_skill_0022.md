---
name: annotation-metadata-revision-date-null-handling
description: When constructing a revision metadata object (e.g., AnnotationRevisionMetadata)
  that parses a revision number from a custom annotation, ensure the test validates
  that a null or invalid revision number does not crash the constructor — it should
  either throw a meaningful exception or handle it gracefully rather than triggering
  a NullPointerException or NumberFormatException.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# annotation-metadata-revision-date-null-handling

## Instructions

# Annotation Revision Metadata Null Handling

## Instructions

- WHEN the TG encounters a metadata class that wraps a custom annotation (like `AnnotationRevisionMetadata`) and extracts a revision number/date from annotation fields (e.g., via `annotation.value()` or `annotation.revision()`)
- THEN it should write a test that passes a null/invalid value for the revision attribute of the custom annotation and verifies that:
  1. The constructor/method throws an `IllegalArgumentException` (or another documented checked exception) with a clear message — not a `NullPointerException` or `NumberFormatException`
  2. OR if the API contract says null values are allowed, verify the resulting object exposes a sensible default (e.g., `null` or `Optional.empty()`)

- Common pitfalls:
  - Testing only the "happy path" where the annotation attribute is always a valid number
  - Assuming `Long.valueOf(null)` or `Long.parseLong(null)` will produce a helpful error, when in fact they throw raw `NumberFormatException`
  - Not testing the `AnnotationRevisionMetadata` constructor with a mock/stub annotation that returns `null` for the revision number

- Example of correct test (using Mockito-style mock or inline annotation):
```java
@Test(expected = IllegalArgumentException.class)
public void rejectsNullRevision() {
    RevisionAnnotation annotation = mock(RevisionAnnotation.class);
    when(annotation.value()).thenReturn(null);
    new AnnotationRevisionMetadata<>(annotation, RevisionAnnotation.class);
}
```

- Example of incorrect test (missing null case):
```java
@Test
public void exposesRevisionNumber() {
    RevisionAnnotation annotation = mock(RevisionAnnotation.class);
    when(annotation.value()).thenReturn(1L);  // Only tests valid value
    RevisionMetadata<?> metadata = new AnnotationRevisionMetadata<>(annotation, RevisionAnnotation.class);
    assertEquals(1L, metadata.getRevisionNumber());
}
```