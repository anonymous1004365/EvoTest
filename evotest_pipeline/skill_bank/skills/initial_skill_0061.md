---
name: try-catch-custom-exception-ordering
description: When extending CtTypeReference-like logic that maps custom exception
  types to catch blocks, the TG should test that exceptions (including custom types)
  are matched in the correct multi-catch block ordering. This skill is for catching
  type-reference equality bugs that cause wrong catch-block assignment in try-catch
  with multiple custom exception types.
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
- TYPE_REFERENCE_EQUALS
- INHERITANCE_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# try-catch-custom-exception-ordering

## Instructions

# Try-Catch Custom Exception Ordering

## Instructions

- WHEN the TG encounters code that processes try-catch blocks and maps exception types (CtTypeReference or similar type representations) to catch-block parameters — especially in a multi-catch (multiple exception types per catch clause) scenario
- THEN the TG should write a test that:
  1. Creates a method with a try-catch that has multiple catch blocks, each catching different custom exception types (e.g., `CustomExceptionA`, `CustomExceptionB` that extend `Exception`)
  2. Verifies that each custom exception type is assigned to the **correct** catch block according to the source ordering (not swapped or duplicated)
  3. Asserts that the number of mapped catch blocks equals the number of catch blocks in the source
  4. Asserts that each mapped catch block's caught exception types match the source types exactly, preserving order
- Common pitfalls to avoid:
  - Testing only with standard Java exception types like `IOException`, `Exception` — custom types may expose equality/hashCode bugs in type reference logic
  - Assuming multi-catch ordering is preserved when type references have custom equality behavior
  - Not checking that exception types from different catch blocks aren't merged or swapped
- Example correct approach:
  ```java
  // Given a method with:
  // try { ... }
  // catch (CustomExceptionA | CustomExceptionB e) { ... }
  // catch (CustomExceptionC e) { ... }
  
  // Then verify:
  // catchBlocks.get(0).caughtTypes contains [CustomExceptionA, CustomExceptionB] in order
  // catchBlocks.get(1).caughtTypes contains [CustomExceptionC]
  ```
- Example incorrect approach:
  ```java
  // WRONG: Only checking total count of catch blocks or only using IOException
  assertEquals(2, catchBlocks.size()); // insufficient — doesn't verify type assignment
  ```