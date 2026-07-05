---
name: hybrid-hash-join-spill-condition
description: When testing hash join partition spilling code, verify that spillPartition()
  is not called on partitions with fewer than 2 build-side memory buffers, as this
  violates an internal invariant and throws an IllegalStateException.
code_tags:
- STATE_MUTATION
- BOUNDARY_CHECK
- RESOURCE_MANAGEMENT
test_pattern: EXCEPTION_TEST
---

# hybrid-hash-join-spill-condition

## Instructions

# Hybrid Hash Join Spill Condition Validation

## Instructions

- WHEN the TG encounters code that manages spilling of `HashPartition` objects in a `MutableHashTable` (hybrid hash join), particularly the `spillPartition()` method or the `nextRecord()` / `nextRecordWithIndex()` iteration path that triggers spilling
- THEN it should write a test that verifies spilling only occurs on partitions with at least 2 `buildSideMemory` segments. The `HashPartition.spillPartition(...)` method explicitly checks `if (this.buildSideMemory.numOccupiedMemSegments < 2)` and throws `new IllegalStateException("Request to spill a partition with less than two buffers.")`. The test must reproduce the exact scenario where a partition with fewer than 2 buffers gets selected for spilling — this typically happens when the hash table fills up and `spillPartition()` selects a partition whose `buildSideMemory` has been exhausted by repeated insertions without sufficient segment returns.
- Include concrete values: use a memory pool of exactly the size needed to force the hash table into a state where only 1 build-side segment remains on one partition. The test should use `MutableHashTable<IntValue, IntValue>` with a custom `TypeSerializer` and `TypeComparator`, insert enough entries to trigger spill, and catch the `IllegalStateException` with the message "Request to spill a partition with less than two buffers."
- Common pitfalls to avoid:
  - Only testing with large memory pools that never exhaust build-side segments — the bug only manifests when memory is tight.
  - Not using enough rows to force the hash table's internal partition to fill and trigger the spill selection logic.
  - Forgetting to configure `IOManager` (e.g., `IOManagerAsync`) since spilling requires disk I/O.
  - Assuming the exception will be thrown immediately — it may only occur after inserting many entries and the iteration logic (`nextRecord()`) triggers spill.

### Correct Example (catching the buggy behavior):
```java
@Test
public void testSpillingFreesOnlyOverflowSegments() throws Exception {
    final IOManager ioManager = new IOManagerAsync();
    try {
        final int PAGE_SIZE = 32 * 1024;
        final int NUM_PAGES = 10; // small memory to force tight conditions
        final int NUM_KEYS = 2000; // enough rows to force partition filling

        BinaryVectorGenerator<IntValue, IntValue> gen = new BinaryVectorGenerator<>(
            IntValue.class, IntValue.class, 
            IntValue.class, IntValue.class,
            0, 0,
            new IntValue(0), new IntValue(0),
            PAGE_SIZE, PAGE_SIZE, NUM_PAGES);
        
        HashTableTest.MutableHashTableWithJavaHashMap<IntValue, IntValue> table = 
            new HashTableTest.MutableHashTableWithJavaHashMap<>(
                gen.getBuildSideSerializer(), gen.getProbeSideSerializer(),
                gen.getBuildSideComparator(), gen.getProbeSideComparator(),
                gen.getPairComparator(),
                gen.getMemorySegments(), PAGE_SIZE,
                ioManager);
        
        table.open(
            new HashTableTest.RecordReader(gen.getBuildSideGenerator(NUM_KEYS)),
            new HashTableTest.RecordReader(gen.getProbeSideGenerator(NUM_KEYS)),
            true); // use true for build-side spilling

        IllegalStateException expected = assertThrows(
            IllegalStateException.class,
            () -> {
                // Trigger iteration which may cause spill
                ObjectIterator<IntValue, IntValue> iterator = table.getEntryIterator();
                while (iterator.next() != null) {
                    // consume all entries
                }
            });
        
        assertTrue(expected.getMessage().contains(
            "Request to spill a partition with less than two buffers."));
    } finally {
        ioManager.shutdown();
    }
}
```

### Incorrect Example (won't catch the bug):
```java
@Test
public void testSpillingInsufficientMemory() throws Exception {
    // Bug: using too much memory; the bug only appears with tight memory
    final int NUM_PAGES = 100; 
    // ... rest of setup
    // This test will never trigger the bug because partitions always have enough segments
}
```