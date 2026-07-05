---
name: batch-scanner-column-filter-proxy
description: WHEN the TG sees a proxy layer that translates Thrift BatchScanOptions
  with ScanColumn filters into Accumulo core Column objects, THEN test that column
  family only, column family+qualifier, and mixed column sets all return the correct
  filtered count of entries. This skill catches bugs where the column filter translation
  silently drops or duplicates entries in the proxy server.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# batch-scanner-column-filter-proxy

## Instructions

# Batch Scanner Column Filter Translation in Proxy

## Instructions

- WHEN the TG encounters code that converts Thrift `BatchScanOptions.columns` (a list of `ScanColumn` objects with optional `colFamily` and `colQualifier` ByteBuffer fields) into Accumulo core `Column` objects (e.g., `new Column(family, qualifier)` or `Collections.singleton(new Column(family, qualifier))`) inside a `createBatchScanner`-like proxy method
- THEN the TG should write a parametric test that:
  1. Inserts a large, deterministic set of entries (e.g., 100,000 entries) with column families cycling on/off a pattern (e.g., "cf0" and "cf1" alternating via `i % 2`)
  2. Creates a `BatchScanOptions` with `columns` set to a `ScanColumn` that specifies only a `colFamily` (no `colQualifier`)
  3. Calls the proxy's `createBatchScanner`, iterates all results via `nextK`, and verifies the total count equals exactly half the inserted count (e.g., 50,000)
  4. Repeats with a `ScanColumn` that specifies both `colFamily` AND `colQualifier` — the expected count depends on how many entries match both (e.g., with `i % 2` pattern and both cf0+cq0, expect 50,000)
  5. Repeats with no columns at all (null/empty columns list) — expects all entries returned (100,000)
- Include a column-family-only version (the type that failed) and a full-column version as separate test methods or parameterized variations
- Common pitfalls to avoid:
  - Testing only with full column specifiers (both family and qualifier) while missing the column-family-only case, where the bug manifests
  - Using too few entries — the bug might only manifest with large batches that trigger pagination/iteration paths
  - Not verifying the "no columns" case (empty/null columns list) as a baseline — this helps isolate whether the issue is in filter application or iteration logic

### Correct approach (catches the bug):

```java
// Insert 100000 entries with cf0/cf1 alternating
Map<ByteBuffer,List<ColumnUpdate>> mutations = new HashMap<>();
String format = "%1$05d";
for (int i = 0; i < 100000; i++) {
  addMutation(mutations, String.format(format, i), "cf" + (i % 2), "cq" + (i % 2), Util.randString(10));
  if (i % 1000 == 0 || i == 99999) {
    tpc.proxy().updateAndFlush(userpass, testtable, mutations);
    mutations.clear();
  }
}

// Test with column family only
BatchScanOptions options = new BatchScanOptions();
ScanColumn sc = new ScanColumn();
sc.colFamily = ByteBuffer.wrap("cf0".getBytes());
options.columns = Collections.singletonList(sc);
String cookie = tpc.proxy().createBatchScanner(userpass, testtable, options);

int count = 0;
boolean hasNext = true;
while (hasNext) {
  ScanResult kvList = tpc.proxy().nextK(cookie, 1000);
  count += kvList.getResultsSize();
  hasNext = kvList.isMore();
}
assertEquals(50000, count);
```

### Incorrect approach (misses the bug):

```java
// Only tests with full column (family + qualifier)
ScanColumn sc = new ScanColumn();
sc.colFamily = ByteBuffer.wrap("cf0".getBytes());
sc.colQualifier = ByteBuffer.wrap("cq0".getBytes());
options.columns = Collections.singletonList(sc);
// This test might pass even when column-family-only filtering is broken
```