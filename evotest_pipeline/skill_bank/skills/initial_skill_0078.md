---
name: file-length-overflow-detection
description: Helps detect integer overflow bugs in fileLength() methods that compute
  file sizes using int arithmetic instead of long arithmetic. Apply when testing Directory
  implementations that combine segment sizes into a total file length.
code_tags:
- OVERFLOW
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# file-length-overflow-detection

## Instructions

# File Length Integer Overflow Detection

## Instructions

- WHEN the TG encounters a method that calculates a file length by summing individual segment/chunk sizes (e.g., iterating over entries and accumulating a `long` result using `int`-based operations or using `int` casts of `long` values)
- THEN the TG should test with file sizes that exceed `Integer.MAX_VALUE` (2,147,483,647 bytes ≈ 2GB):
  - Create a file whose logical length is greater than `Integer.MAX_VALUE` (e.g., 2,976,743,424 bytes)
  - Hard-code expectations: write a known total file length as a `long` literal (e.g., `2976743424L`)
  - Call `directory.fileLength("testfile")` and assertEquals with the known long value
  - Expect an assertion failure on the buggy version: the int-overflowed value will be negative (e.g., `-1318223872`) instead of the correct long value (e.g., `2976743424L`)
- WHEN writing such a test, the TG should NOT:
  - Use `int` arithmetic to compute the expected file length (this will overflow in the test itself)
  - Rely on the implementation's own methods to compute the expected value (circular logic)
  - Only test with small files under 2GB (misses the overflow case entirely)
- Common pitfalls:
  - Computing expected values with expressions like `largeValue1 + largeValue2` without casting to `long` first (use `largeValue1 + (long)largeValue2` or `largeValue1L + largeValue2L`)
  - Forgetting that intermediate `int` multiplication or addition overflows before being assigned to a `long` variable
  - Testing only with sizes that fit comfortably within int range
- Example of correct test code (simplified):
  ```java
  @Test
  public void testFileLengthOverflow() throws IOException {
      // Setup: create a file whose total size exceeds Integer.MAX_VALUE
      // e.g., write segments/chunks totaling 2976743424 bytes
      long expectedFileLength = 2976743424L; // > Integer.MAX_VALUE
      
      long actualFileLength = directory.fileLength("testfile");
      
      assertEquals("fileLength overflowed int arithmetic", expectedFileLength, actualFileLength);
  }
  ```
- Example of incorrect test code:
  ```java
  @Test
  public void testFileLength() throws IOException {
      // BAD: creates file with small size, no overflow scenario
      // BAD: computing expected with int arithmetic
      int expected = 1000 + 2000; // overflow not tested
      long actual = directory.fileLength("testfile");
      assertEquals(expected, actual); // Only tests non-overflow case
  }
  ```