---
name: bulk-file-mutation-txid-validation
description: When a mutation writes to the BulkFileColumnFamily in system metadata
  tables, the transaction ID must correspond to an active transaction and be paired
  with a corresponding DataFileColumnFamily entry. Test both inactive txids, missing
  file pairs, and txids that throw exceptions from the Arbitrator.
code_tags:
- VALIDATION
- EDGE_CASE_INPUT
- ARGUMENT_VALIDATION
- BULK_TX_MUTATION_CHECK
test_pattern: STATE_TEST
---

# bulk-file-mutation-txid-validation

## Instructions

# Bulk File Mutation Transaction ID Validation

## Instructions

- WHEN the TG encounters a Constraint implementation that validates bulk file mutations on system metadata tables by checking transaction IDs against an Arbitrator
- THEN the TG should write tests that exercise all branches of the validation logic:

  1. **Test with an inactive transaction ID**: Create a mutation with a bulk file column family entry whose value is a transaction ID (e.g., `"12345"`) that is **not alive** according to the Arbitrator. The Constraint should return a violation (error code 8). Verify the violation is present.

  2. **Test with an active transaction ID that throws an exception**: Create a mutation with a bulk file entry whose value is a transaction ID (e.g., `"9"`) that causes the Arbitrator to throw a RuntimeException. The Constraint should catch this exception and return a violation (error code 8). Verify the violation is present.

  3. **Test with an active transaction ID and paired DataFileColumnFamily entry**: Create a mutation that has both a BulkFileColumnFamily entry (with an active txid, e.g., `"5"`) AND a DataFileColumnFamily entry for the same file path. The Constraint should return null (no violations). Verify no violations.

  4. **Test with an active transaction ID but no corresponding DataFileColumnFamily entry**: Create a mutation with only a BulkFileColumnFamily entry (active txid) but no DataFileColumnFamily entry. The Constraint should return a violation (error code 8). Verify the violation is present.

  5. **Test with two different active transaction IDs each with their own DataFileColumnFamily entry**: Create a mutation with two bulk file entries (different txids, both active), each with a corresponding DataFileColumnFamily entry. The Constraint should return a violation (error code 8) because there are multiple bulk-load transactions. Verify the violation.

  6. **Test with one active transaction ID and two DataFileColumnFamily entries**: Create a mutation with two bulk file entries using the same active txid, each with a paired DataFileColumnFamily entry. The Constraint should return null (no violations). Verify no violations.

- WHEN overriding `getArbitrator()` in tests, ensure the mock Arbitrator:
  - Returns `transactionAlive(type, tid) == true` only for specific known alive txids (e.g., `5` and `7`)
  - Returns `transactionAlive(type, tid) == false` for all other txids
  - Throws RuntimeException for a specific reserved txid (e.g., `9`) to test exception handling
  - Returns `transactionComplete(type, tid) == true` only for txids that are NOT alive

- WHEN testing bulk file constraints, use a **subclass** of the Constraint (e.g., `TestMetadataConstraints`) that overrides `getArbitrator()` to provide controlled test behavior. Do NOT test against the real Arbitrator implementation.

- Common pitfalls to avoid:
  - **Testing only one path through the validation logic**: The bulk file check has multiple branches (inactive txid, exception, multiple txids, missing file pairs). Test all branches.
  - **Using a real Arbitrator in tests**: The real Arbitrator depends on ZooKeeper state. Always mock/override `getArbitrator()`.
  - **Forgetting to add the DataFileColumnFamily entry when testing for violations**: The bug may involve the validation passing when it should fail because a file pair is missing. Ensure your test covers the case where a bulk file column exists without a corresponding data file column.
  - **Using invalid row keys**: The row key must be valid (e.g., `"0;foo"`) to avoid triggering other validation errors that would mask the bulk file validation result.
  - **Checking only for `assertNotNull(violations)`**: Always verify the **specific violation code** (e.g., `assertEquals(Short.valueOf((short) 8), violations.get(0))`) to ensure the correct constraint is being triggered.

### Correct Test Example (Mock Arbitrator)

```java
static class TestMetadataConstraints extends MetadataConstraints {
  @Override
  protected Arbitrator getArbitrator() {
    return new Arbitrator() {
      @Override
      public boolean transactionAlive(String type, long tid) throws Exception {
        if (tid == 9) throw new RuntimeException("txid 9 reserved for future use");
        return tid == 5 || tid == 7;
      }
      @Override
      public boolean transactionComplete(String type, long tid) throws Exception {
        return tid != 5 && tid != 7;
      }
    };
  }
}

@Test
public void testBulkFileCheck() {
  MetadataConstraints mc = new TestMetadataConstraints();
  
  // inactive txid should produce violation 8
  Mutation m = new Mutation(new Text("0;foo"));
  m.put(TabletsSection.BulkFileColumnFamily.NAME, new Text("/someFile"), new Value("12345".getBytes()));
  m.put(DataFileColumnFamily.NAME, new Text("/someFile"), new DataFileValue(1, 1).encodeAsValue());
  List<Short> violations = mc.check(null, m);
  assertNotNull(violations);
  assertEquals(Short.valueOf((short) 8), violations.get(0));
  
  // txid that throws exception should produce violation 8
  m = new Mutation(new Text("0;foo"));
  m.put(TabletsSection.BulkFileColumnFamily.NAME, new Text("/someFile"), new Value("9".getBytes()));
  m.put(DataFileColumnFamily.NAME, new Text("/someFile"), new DataFileValue(1, 1).encodeAsValue());
  violations = mc.check(null, m);
  assertNotNull(violations);
  assertEquals(Short.valueOf((short) 8), violations.get(0));
  
  // active txid with file pair should pass
  m = new Mutation(new Text("0;foo"));
  m.put(TabletsSection.BulkFileColumnFamily.NAME, new Text("/someFile"), new Value("5".getBytes()));
  m.put(DataFileColumnFamily.NAME, new Text("/someFile"), new DataFileValue(1, 1).encodeAsValue());
  violations = mc.check(null, m);
  assertNull(violations);
  
  // active txid without file pair should fail
  m = new Mutation(new Text("0;foo"));
  m.put(TabletsSection.BulkFileColumnFamily.NAME, new Text("/someFile"), new Value("5".getBytes()));
  violations = mc.check(null, m);
  assertNotNull(violations);
  assertEquals(Short.valueOf((short) 8), violations.get(0));
}
```

### Incorrect Test Example

```java
// BAD: Only tests one case (active txid with file), missing all other branches
@Test
public void testBulkFile() {
  MetadataConstraints mc = new TestMetadataConstraints();
  Mutation m = new Mutation(new Text("0;foo"));
  m.put(TabletsSection.BulkFileColumnFamily.NAME, new Text("/someFile"), new Value("5".getBytes()));
  m.put(DataFileColumnFamily.NAME, new Text("/someFile"), new DataFileValue(1, 1).encodeAsValue());
  assertNull(mc.check(null, m));
  // Missing: inactive txid, exception-throwing txid, missing file pair, multiple txids
}
```