---
name: mutation-put-validation-catch
description: ''
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# mutation-put-validation-catch

## Instructions

# Mutation PUT Validation Test Skill

## Instructions

- WHEN the TG encounters a `Mutation` object being constructed or written via a `BatchWriter` implementation (e.g., `MockBatchWriter`, `BatchWriter`), and the validation logic checks for invalid row keys
- THEN the TG should write a test that:
  1. Creates a `Mutation` with an invalid row key (e.g., `new Mutation(new byte[]{})` — an empty byte array for the row ID)
  2. Adds at least one column update to the mutation (e.g., `mutation.put(new Text("cf"), new Text("cq"), new Value("val".getBytes()))`)
  3. Passes the mutation to the `BatchWriter.addMutation()` method (or similar write path)
  4. Expects a specific exception to be thrown (e.g., `IllegalArgumentException`) during the `addMutation()` call

- The test must verify that the exception is thrown **at write time** (when `addMutation()` or `addMutations()` is called), NOT at mutation construction time (e.g., `new Mutation(new byte[]{})` itself may not throw)

- Common pitfalls to avoid:
  - Do NOT test only with `null` row keys — empty row keys (`new byte[]{}`) are a distinct invalid case and often not caught by null checks
  - Do NOT stop at mutation construction; ensure the write path (`addMutation`) is exercised
  - Do NOT assume the exception type is `IllegalArgumentException` without checking the actual validation code
  - Do NOT forget to add column data to the mutation via `put()` before testing, as some code paths skip validation for empty mutations

**Correct example** (Java/JUnit 4 style):
```java
@Test(expected = IllegalArgumentException.class)
public void testAddEmptyRowMutation() throws Exception {
    Mutation emptyRowMutation = new Mutation(new byte[]{});
    emptyRowMutation.put(new Text("cf"), new Text("cq"), new Value("value".getBytes()));
    Connector conn = new MockConnector();
    BatchWriter bw = conn.createBatchWriter("table", new BatchWriterConfig());
    bw.addMutation(emptyRowMutation);
    bw.close();
}
```

**Incorrect example** (does NOT reach the write path, may pass incorrectly on buggy code):
```java
@Test(expected = IllegalArgumentException.class)
public void testEmptyRowMutation() throws Exception {
    // This only tests the constructor, not the write validation!
    Mutation m = new Mutation(new byte[]{});
    // The buggy code might allow this Mutation to exist but reject it at write time
}
```