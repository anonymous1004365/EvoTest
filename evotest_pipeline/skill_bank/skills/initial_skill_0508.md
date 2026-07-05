---
name: list-record-empty-size
description: WHEN testing writeList operations with ListRecord, THEN test with an
  empty list to verify the segment writer handles size=0 correctly without throwing
  ArrayIndexOutOfBoundsException or similar errors. This is often missed because empty
  collections are boundary cases.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: PARAMETRIC_TEST
---

# list-record-empty-size

## Instructions

# List Record Empty Size Handling

## Instructions

WHEN testing a `SegmentWriter.writeList()` method that accepts a `List<RecordId>` and creates a `ListRecord` internally:

- THEN include a test case with an **empty list** (`Collections.emptyList()` or `new ArrayList<>()`) passed to `writeList()`
- Verify that the `writeList()` call completes without throwing `ArrayIndexOutOfBoundsException`, `IllegalArgumentException`, or `NegativeArraySizeException`
- Verify that the returned `RecordId` is not null
- Verify that the resulting record can be read back (e.g., via `SegmentParser.readList()` or similar reader method) and returns an empty list or the expected empty state
- Test with both the list writer path and any intermediate layers that call it (e.g., `DefaultSegmentWriter.writeList()`)

**Common pitfalls to avoid:**
- Do NOT assume all callers always pass non-empty lists — the API accepts any `List<RecordId>`, including empty ones
- Do NOT skip testing empty lists just because the production code only passes multi-element lists today — the contract allows empty lists
- Do NOT test only with `null` input and forget about the empty list boundary case
- Do NOT assume that because a method works with size=1 it works with size=0 — the internal logic often differs (e.g., array allocation, index calculations)

**Correct example:**
```java
@Test
public void testWriteEmptyList() throws Exception {
    List<RecordId> emptyList = Collections.emptyList();
    RecordId listId = writer.writeList(emptyList);
    assertNotNull(listId);
    // Then verify it can be read back
    List<RecordId> readBack = parser.readList(listId);
    assertTrue(readBack.isEmpty());
}
```

**Incorrect example (what might happen without this skill):**
```java
// Only tests non-empty lists, missing the boundary case
@Test
public void testWriteListWithSingleElement() throws Exception {
    List<RecordId> list = Arrays.asList(someRecordId);
    RecordId listId = writer.writeList(list);
    assertNotNull(listId);
}
// Empty list is never tested — bug with ListRecord.of(0) or similar survives
```