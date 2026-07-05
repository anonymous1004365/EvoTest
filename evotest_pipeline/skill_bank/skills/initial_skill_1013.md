---
name: replication-table-iterator-configuration
description: Teaches how to verify that a ReplicationTableUtil-like utility sets up
  iterators (like StatusCombiner) on the metadata table. Use when testing code that
  attaches combiners or iterators to a table's iterator settings.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- STATUS_COMBINER_ITERATOR_SETUP
- REPLICATION_TABLE_CONFIG
test_pattern: PARAMETRIC_TEST
---

# replication-table-iterator-configuration

## Instructions

# Replication Table Iterator Configuration

## Instructions

- WHEN the TG encounters a utility method that configures iterators on a table (e.g. `ReplicationTableUtil` adding a `StatusCombiner` with a specific name like `"replcombiner"` and priority like `9`)
- THEN the TG should write a test that:
  1. Creates an `AccumuloConfiguration` (or `ConfigurationCopy`) with `ReplicationTableUtil.REPLICATION_TABLE_CONFIG` set to an otherwise-unused table ID (e.g. `"!0"`)
  2. Creates a `TabletServerConfiguration` wrapping that configuration
  3. Creates a mock `KeyExtent` with that table ID
  4. Invokes the utility method (e.g. `ReplicationTableUtil.updateFiles(...)`)
  5. Checks that the resulting mutation includes an `IteratorSetting` with:
     - Priority exactly `9`
     - Name exactly `"replcombiner"`
     - Class exactly `StatusCombiner.class.getName()` (i.e. `"org.apache.accumulo.server.replication.StatusCombiner"`)
     - The column family on which the iterator is set matches `MetadataSchema.ReplicationSection.COLF` (value: `"stat"`)
  6. Also verifies that re-invocation of the method does NOT add a duplicate combiner — i.e. when iterators already contain `"replcombiner"`, the method should skip adding it again
  7. On the buggy version, the test should expect that the combiner is missing from the mutation or set on the wrong column family; on the fixed version, the combiner should be present and correct

- Common pitfalls to avoid:
  - Testing only that a table exists or only that configuration is read, without verifying the exact iterator settings
  - Forgetting to check the column family on which the iterator is applied
  - Only checking one invocation path and missing the "already configured" skip logic (idempotency)
  - Using the wrong table ID — the test must use the actual config key `ReplicationTableUtil.REPLICATION_TABLE_CONFIG`

### Correct (minimal pseudocode)
```java
// Given
ConfigurationCopy config = new ConfigurationCopy();
config.set(ReplicationTableUtil.REPLICATION_TABLE_CONFIG, "!0");
TabletServerConfiguration tsc = new TabletServerConfiguration(config);
KeyExtent extent = new KeyExtent("!0", null, null);
BatchWriter bw = mock(BatchWriter.class);
Mutation m = captureMutation(bw);

// When
ReplicationTableUtil.updateFiles(tsc, extent, "file.rf", status, bw);

// Then
IteratorSetting actual = m.getIteratorSetting(ColumnFamily.of("stat"));
assertNotNull(actual);
assertEquals(9, actual.getPriority());
assertEquals("replcombiner", actual.getName());
assertEquals(StatusCombiner.class.getName(), actual.getIteratorClass());
```

### Incorrect (missing iterator verification)
```java
// BAD: Only checks that the mutation is written, not the iterator setup
ReplicationTableUtil.updateFiles(tsc, extent, "file.rf", status, bw);
verify(bw).addMutation(any(Mutation.class)); // Does not catch missing combiner!
```