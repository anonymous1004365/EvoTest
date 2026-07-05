---
name: import-template-null-type-check
description: When sorting or ordering imports by comparing type references extracted
  from a HashMap, the type may be null if removed or not yet added, leading to NullPointerException.
  Test that ordering operations handle missing/null values gracefully.
code_tags:
- VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
- IMPORT_ORDER_HASHMAP_NULL_CHECK
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# import-template-null-type-check

## Instructions

# Import Template Null Type Check

## Instructions

- WHEN the TG encounters code that maintains a `HashMap<String, CtTypeReference>` (or similar generic map) to track imports, where entries are added/removed dynamically, and there is logic that reads from this map (e.g., `imports.get(name)`) to compare or sort types
- THEN the TG should write a test that:
  1. Adds entries to the import map with both `String` keys and `CtTypeReference` values
  2. Removes one or more entries from the map (e.g., via a method like `removeImport` or by clearing and re-adding)
  3. Calls a method that iterates over the map entries and compares type references (e.g., sorting by `getSimpleName()` or `toString()`) — this is where the bug manifests as a NullPointerException
  4. The test should expect the operation to complete without throwing `NullPointerException`, even when some map values are temporarily null/absent

- The specific bug pattern: when constructing a sorted key string like `typeRef.getSimpleName()` or calling `.toString()` on a value retrieved from `imports.get(name)`, if that value is `null`, a NullPointerException is thrown. The fix involves checking for null before accessing the value, or ensuring the map never has null values at the point of access.

- **Common pitfalls to avoid:**
  - Testing only the happy path where all entries exist in the map — the bug manifests precisely when entries are missing/removed
  - Testing the add/remove logic in isolation without triggering the sort/compare path that reads from the map
  - Forgetting that HashMap.get() returns null for absent keys — the null is not the key but the value
  - Assuming the map uses a ConcurrentHashMap or similar — the issue is not concurrency but null-unsafe value access

- **Correct test example (conceptual)**:
  ```java
  // Setup: add imports
  importHandler.addImport("java.util.List", someTypeRef);
  importHandler.addImport("java.util.Map", anotherTypeRef);
  
  // Remove one to trigger null-in-map scenario
  importHandler.removeImport("java.util.Map");
  
  // This should NOT throw NullPointerException
  importHandler.sortImports(); // the sorting method reads from the map
  ```

- **Incorrect test example**:
  ```java
  // Only tests the happy path
  importHandler.addImport("java.util.List", someTypeRef);
  importHandler.sortImports(); // works fine, all values present
  
  // OR: tests only add/remove without the sort/compare path
  importHandler.addImport("java.util.List", someTypeRef);
  importHandler.removeImport("java.util.List"); // no NPE here, just removes
  ```