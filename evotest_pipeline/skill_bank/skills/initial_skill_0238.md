---
name: mutation-equals-then-put-state
description: When a mutable object has internal serialization/optimization triggered
  by read methods like equals() or hashCode(), calling mutator methods after reads
  can leave the object in an inconsistent state. Use this skill to test that calling
  mutating methods after equals()/hashCode() on mutable collections does not throw
  exceptions or corrupt internal state.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# mutation-equals-then-put-state

## Instructions

# Mutation State Corruption After Read Methods

## Instructions

- WHEN the TG encounters a class with mutable internal state (e.g., a Mutation, a collection, or a builder) that has a `serialize()`, `freeze()`, or similar internal optimization triggered by read methods like `equals()`, `hashCode()`, or `toString()`,  
- THEN the TG should write a test that:
  1. Creates an instance of the mutable class
  2. Calls a read-only method (e.g., `equals()`, `hashCode()`, or `compareTo()`) on it
  3. **After** that read, calls a mutating method (e.g., `put()`, `add()`, `set()`) that modifies the internal state
  4. Verifies that the mutating method does NOT throw an `IllegalStateException`, `IllegalArgumentException`, `NullPointerException`, or any other runtime exception
  5. Also verifies that the mutation was actually applied and the object state is correct afterwards (e.g., by reading back the value)

- **Common pitfalls** to avoid:
  - Testing only with a single mutation without calling `equals()`/`hashCode()` first — this misses the bug entirely
  - Testing `equals()` after mutation (which works fine) instead of testing mutation **after** `equals()` (which breaks)
  - Assuming that `equals()` is purely read-only and cannot alter internal state — some implementations serialize or freeze state during `equals()`/`hashCode()`
  - Forgetting to verify the mutation was applied (only checking no exception is not enough)

- **Example of a correct test** (TypeScript-style pseudocode):
  ```typescript
  // When Mutation.equals() triggers serialize(), further puts should still work
  function testPutAfterEquals() {
    let m = new Mutation("row1");
    // Add some initial data
    m.put("cf1", "cq1", "val1");
    // Call equals() which may trigger internal serialization
    let other = new Mutation("row2");
    m.equals(other);
    // Now try to put more data after equals() — buggy version throws IllegalStateException
    m.put("cf2", "cq2", "val2");  // Should not throw!
    // Verify the put actually took effect
    assertEquals(2, m.getUpdates().size());
    // Additional verification: read back the new entry
    assertEquals("val2", /* get value for cf2:cq2 */);
  }
  ```

- **Example of an INCORRECT test** (missing the key sequence):
  ```typescript
  // BUG: This test passes even on the buggy version
  function testPutBeforeEquals() {
    let m = new Mutation("row1");
    m.put("cf1", "cq1", "val1");
    m.put("cf2", "cq2", "val2"); // Putting before equals works fine
    m.equals(other); // equals is called after all mutations — no crash
    // This never discovers the bug!
  }
  ```

- **What to verify**: The test should assert that:
  - No exception of type `IllegalStateException`, `RuntimeException`, or any subclass is thrown when calling the mutating method after the read method
  - The mutation was actually applied (e.g., by checking the count of entries, or reading back a specific value that was just added)

- **Abstract template for the test pattern**:
  1. Instantiate object with mutable internal state
  2. Add some initial data to populate the state
  3. Call a read/query method (equals, hashCode, toString, compareTo, etc.)
  4. Call a mutating method (add, put, set, remove, append, etc.) — expect NO exception
  5. Assert the mutation took effect by querying the object