---
name: default-constructor-npe-position
description: ''
code_tags:
- STATE_MUTATION
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# default-constructor-npe-position

## Instructions

# Default Constructor NullPointer on Position/Coordinate Fields

## Instructions

- **WHEN** the TG encounters a class with a no-arg constructor (either explicit or compiler-generated default constructor) that initializes position, source reference, or coordinate fields (e.g., `sourceStart`, `sourceEnd`, `position`, `SourcePosition` fields) — especially a constructor body that is empty or absent —
  - **THEN** the TG should create a test that:
    1. Instantiates the object using the no-arg constructor (e.g., `new Position()`, `new CtElementImpl()`).
    2. Calls `toString()` or any formatting method that accesses the previously uninitialized position/coordinate fields.
    3. Asserts that the call does **NOT** throw a `NullPointerException` and that the output string contains meaningful default values (e.g., `"(0,0)"` instead of `"null"`), OR that the fields are set to non-null sentinels after construction.

- **Common Pitfalls to avoid:**
  - Testing only parameterized constructors and ignoring the no-arg constructor.
  - Testing the no-arg constructor only with getter methods (which may return `null`) and missing the `toString()` trigger.
  - Assuming a no-arg constructor is safe because it has no visible body — the compiler-generated default constructor may leave all fields uninitialized (`null` for reference types, `0` for primitives).
  - Not checking whether the class mixes auto-generated and handwritten constructors — the presence of one explicit constructor removes the automatic generation of defaults.

- **Example (Correct approach):**
  ```java
  // Given a class like:
  // class Position { String sourceStart, sourceEnd; ... }
  // With a no-arg constructor that fails to init sourceStart/sourceEnd
  @Test
  public void defaultConstructorNoNpeTest() {
      // Create using no-arg constructor
      Position pos = new Position();
      // Trigger formatting: toString() iterates over sourceStart/sourceEnd
      String result = pos.toString();
      // Should not throw NPE, should show "(0,0)" or similar sentinel
      assertNotNull(result);
      assertTrue(result.contains("0"));
  }
  ```

- **Example (Wrong approach):**
  ```java
  // BAD: Only tests parameterized constructor, misses the bug
  @Test
  public void parameterizedConstructorTest() {
      Position pos = new Position("file", 1, 2, 3, 4);
      assertEquals("file (1,2)-(3,4)", pos.toString()); // passes, but doesn't cover default ctor
  }
  ```

- **What the test should catch on the buggy version:**
  - `NullPointerException` at the point where the `toString()` (or similar) method accesses uninitialized reference-typed fields (e.g., `sourceStart.toString()`, `sourceEnd.toString()`, concatenation with null).
  - On the fixed version, the same test should pass cleanly because those fields are initialized to non-null defaults in the no-arg constructor body or at their declaration site.