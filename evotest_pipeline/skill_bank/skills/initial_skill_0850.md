---
name: journal-entry-key-idempotent-validation
description: When testing journal entry key generation, verify that calling getIdForJournalEntry
  multiple times with the same arguments returns consistent results. Mutating shared
  state (like a counter or IdType mapping) during key computation can corrupt subsequent
  keys, so test both the first call AND subsequent calls with the same inputs.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# journal-entry-key-idempotent-validation

## Instructions

# Journal Entry Key Idempotency Validation

## Instructions

- WHEN a method (e.g. `getIdForJournalEntry`) generates a journal entry key using a combination of:
  - A `Revision` object (with branch flag, timestamp, counter)
  - A stored document ID / `IdType` mapping
  - Shared mutable state (e.g. a static/instance field like `previousEntryId` that is updated during key computation)
- THEN the TG MUST test that calling the method multiple times with the **same inputs** produces the **same output**. Specifically:
  1. Call `getIdForJournalEntry(revision1)` — store the result
  2. Call `getIdForJournalEntry(revision2)` — store the result
  3. Call `getIdForJournalEntry(revision1)` again — **verify it equals the first call's result**
  4. Verify `result1` ≠ `result3` fails the test (caught by assertion)
- The bug manifests because shared mutable state (e.g. `previousEntryId` being overwritten on every call) corrupts the deterministic mapping from `(machineId, revision_timestamp, revision_counter, branch_flag)` → entry key, leading to **duplicate or inconsistent keys**.

**Common pitfalls:**
- Testing only one call to the key generation method (does not detect state mutation)
- Testing only with `null` or zero-value revision fields
- Using a fresh instance of the object for each call (state mutation is only visible on a shared instance)
- Not verifying that the same revision always maps to the same key

**Correct test pattern:**
```java
Revision r1 = new Revision(1, 0, 1); // revision(ts, counter, machineId)
Revision r2 = new Revision(2, 0, 1);

String key1 = entry.getIdForJournalEntry(r1);
String key2 = entry.getIdForJournalEntry(r2);
String key1_again = entry.getIdForJournalEntry(r1);

assertEquals("Key for r1 must be deterministic", key1, key1_again);
assertNotEquals("Different revisions get different keys", key1, key2);
```

**Incorrect test pattern (misses the bug):**
```java
Revision r1 = new Revision(1, 0, 1);
String key1 = entry.getIdForJournalEntry(r1);
// Only checks the first call — never verifies idempotency
```