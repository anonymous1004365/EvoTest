---
name: mock-update-increment-preservation
description: When testing mock Accumulo implementations with update operations (put/putDelete
  on the same cell), verify that the timestamp ordering correctly resolves to the
  expected value. This skill applies when a mutation updates an existing cell using
  a higher timestamp and the mock should reflect the update rather than retaining
  the old value.
code_tags:
- VALIDATION
- STATE_MUTATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# mock-update-increment-preservation

## Instructions

# Mock Update Increment Preservation

## Instructions

- WHEN the TG encounters code that performs a `Mutation.put()` or `Mutation.putDelete()` operation on an existing cell (same row, column family, column qualifier) in a mock Accumulo implementation (e.g., `MockConnector`, `MockTable`, `MockBatchWriter`)
- THEN the TG should write a test that:
  1. Creates a `Mutation` with a row key (e.g., `"r1"`) and puts a value with a specific timestamp (e.g., `m1.put("cf1", "cq1", 1, "v1")`)
  2. Creates a second `Mutation` on the same row that updates the same column with a higher timestamp (e.g., `m2.put("cf1", "cq1", 2, "v2")`)
  3. Adds both mutations to a `BatchWriter` and flushes, then scans the table with a `Scanner`
  4. Asserts that the cell's value is the one from the **higher timestamp** (the update), not the initial insert. In the buggy version, the mock returned the wrong value (expected `"9"` but got `"0"`).

- **Common pitfall to avoid**: Testing only the initial insert (a single `put`) or testing only delete operations. Without this skill, the TG might assume the mock correctly handles all timestamp-based updates. The TG must explicitly test that updating a cell's value with a higher timestamp replaces the old value in the mock.

- **Correct example (test that detects the bug)**:
```java
Connector c = new MockConnector("root", new MockInstance());
c.tableOperations().create("test");
BatchWriter bw = c.createBatchWriter("test", new BatchWriterConfig());

// Insert initial value at timestamp 1
Mutation m1 = new Mutation("r1");
m1.put("cf1", "cq1", 1, "v1");
bw.addMutation(m1);
bw.flush();

// Update the same cell at timestamp 2
Mutation m2 = new Mutation("r1");
m2.put("cf1", "cq1", 2, "v2");
bw.addMutation(m2);
bw.flush();

// Scan and verify the update took effect
Scanner scanner = c.createScanner("test", Authorizations.EMPTY);
int count = 0;
for (Entry<Key,Value> entry : scanner) {
    assertEquals("v2", entry.getValue().toString());
    count++;
}
assertEquals(1, count); // only one entry for the cell, with the updated value
```

- **Incorrect example (test that would pass the buggy version)**:
```java
Connector c = new MockConnector("root", new MockInstance());
c.tableOperations().create("test");
BatchWriter bw = c.createBatchWriter("test", new BatchWriterConfig());

// Only inserting, never updating
Mutation m = new Mutation("r1");
m.put("cf1", "cq1", 1, "v1");
bw.addMutation(m);
bw.flush();

Scanner scanner = c.createScanner("test", Authorizations.EMPTY);
// This passes even on buggy version since there is no update
assertEquals("v1", scanner.iterator().next().getValue().toString());
```