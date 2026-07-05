---
name: metadata-constraint-empty-value-validation
description: When testing metadata table constraint violations, test that mutations
  with empty values on non-ScanFile columns return violation code 6. This catches
  bugs where the empty-value check is missing or incorrectly applied.
code_tags:
- CONSTRAINT_VIOLATION_TYPE
- VALIDATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# metadata-constraint-empty-value-validation

## Instructions

# Metadata Constraint Empty Value Validation

## Instructions

- WHEN the TG encounters a Constraint implementation (like `MetadataConstraints`) that validates `ColumnUpdate` values in a `check(Environment, Mutation)` method
- THEN the TG should specifically test that **non-`ScanFileColumnFamily` columns with empty byte-array values (`new byte[0]` or `"".getBytes()`) trigger violation code 6**
  - Create a `Mutation` with a valid row (e.g., `new Text("0;foo")`)
  - Add a column update using a **valid column family/qualifier** (e.g., `TabletsSection.TabletColumnFamily.PREV_ROW_COLUMN`) but with an empty `Value` (e.g., `new Value("".getBytes())`)
  - Call `mc.check(null, mutation)` and assert the result contains `Short.valueOf((short) 6)`
- WHEN the TG tests the `ScanFileColumnFamily` with empty values
- THEN the TG should verify that **no violation 6 is returned** (empty values are intentionally permitted for scan files)
- WHEN the TG constructs mutations for the `check()` method
- THEN the TG should use the correct column family/qualifier constants from `MetadataSchema.TabletsSection`:
  - For the `PREV_ROW_COLUMN` test: use `TabletsSection.TabletColumnFamily.PREV_ROW_COLUMN.put(mutation, value)`
  - For `DataFileColumnFamily`: use `DataFileColumnFamily.NAME` as the column family
  - For `ScanFileColumnFamily`: use `ScanFileColumnFamily.NAME`
- Common pitfalls to avoid:
  - ❌ Testing only with invalid column families when empty value check should work on **valid** column families too
  - ❌ Forgetting to assert the **specific violation code** (short 6) exists in the violations list
  - ❌ Assuming empty values are universally rejected — `ScanFileColumnFamily` is an explicit exception
  - ❌ Using `null` as the value instead of empty byte array — the code checks `columnUpdate.getValue().length == 0`, not null

### Correct example:
```java
// Mutation with empty value on a valid column (should get violation 6)
Mutation m = new Mutation(new Text("0;foo"));
TabletsSection.TabletColumnFamily.PREV_ROW_COLUMN.put(m, new Value("".getBytes()));
List<Short> violations = mc.check(null, m);
assertNotNull(violations);
assertEquals(1, violations.size());
assertEquals(Short.valueOf((short) 6), violations.get(0));
```

### Incorrect example:
```java
// THIS IS WRONG: uses an invalid column which triggers violation 2 instead of 6
Mutation m = new Mutation(new Text("0;foo"));
m.put(new Text("bad_column"), new Text(""), new Value("".getBytes()));
List<Short> violations = mc.check(null, m);
// violations.get(0) will be 2 (invalid column), not 6 (empty value)
```