---
name: scan-column-family-only-validation
description: When using ScanColumn with only a column family set (no qualifier), test
  that the proxy correctly maps it to a Column with the family set and qualifier empty,
  not null. Apply this skill whenever ColumnTranslator.mapColumns or similar mapping
  logic is used to convert Thrift ScanColumn objects to Accumulo Column objects.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- ARGUMENT_VALIDATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# scan-column-family-only-validation

## Instructions

# Scan Column Family-Only Mapping

## Instructions

- WHEN the TG encounters a `ScanColumn` Thrift object being converted to an Accumulo `Column` object (e.g., in `ColumnTranslator.mapColumns` or equivalent mapping logic)
- THEN the TG should write a test that verifies the mapping of a `ScanColumn` that has ONLY the `colFamily` set (with `colQualifier` being null/not set).
  - The test should create a `ScanColumn` with `colFamily` set to a non-null value and `colQualifier` left as null (default).
  - The test should assert that the resulting `Column` has the `colFamily` correctly set to the expected byte array value.
  - The test should assert that the resulting `Column` has the `colQualifier` set to an **empty byte array** (`new byte[0]`), NOT null.
  - When the buggy code maps a `ScanColumn` with only `colFamily`, it may incorrectly set the `colQualifier` to null instead of an empty byte array `new byte[0]`, causing downstream scanning logic to miss the qualifier filter and return incorrect (duplicate or mismatched) results.
- The TG should avoid the common pitfall of only testing `ScanColumn` objects where BOTH `colFamily` AND `colQualifier` are set. Test the family-only case explicitly.
- The TG should avoid assuming that a null `colQualifier` in the input `ScanColumn` means the output `Column` qualifier should also be null — it should be an empty array.
- Example of a correct test:
  ```java
  @Test
  public void testMapScanColumnFamilyOnly() {
    ScanColumn sc = new ScanColumn();
    sc.setColFamily("cf".getBytes());
    // colQualifier is NOT set (null by default)
    
    Column mapped = ColumnTranslator.mapColumns(sc);
    
    assertArrayEquals("cf".getBytes(), mapped.getColumnFamily());
    assertNotNull("Column qualifier should not be null", mapped.getColumnQualifier());
    assertEquals(0, mapped.getColumnQualifier().length);
  }
  ```
- Example of an incorrect test (which would NOT catch the bug):
  ```java
  @Test
  public void testMapScanColumnBothFields() {
    ScanColumn sc = new ScanColumn();
    sc.setColFamily("cf".getBytes());
    sc.setColQualifier("cq".getBytes());
    
    Column mapped = ColumnTranslator.mapColumns(sc);
    
    assertArrayEquals("cf".getBytes(), mapped.getColumnFamily());
    assertArrayEquals("cq".getBytes(), mapped.getColumnQualifier());
    // This passes on both buggy and fixed code, missing the bug entirely
  }
  ```