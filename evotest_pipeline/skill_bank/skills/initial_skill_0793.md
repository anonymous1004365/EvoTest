---
name: segment-build-exception-handling
description: When validating segment build operations in real-time data managers,
  test that build exceptions are properly handled and do not leave the segment manager
  in an inconsistent or null state. Use this skill when testing methods that invoke
  segment build operations that may throw exceptions.
code_tags:
- VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# segment-build-exception-handling

## Instructions

# Segment Build Exception Handling

## Instructions

- WHEN the TG encounters a method that builds or processes segments in a real-time data manager (e.g., LLRealtimeSegmentDataManager), particularly one that calls a segment build operation that can throw an exception
- THEN it should test that a build exception thrown during the segment build process:
  1. Does NOT leave the segment manager's internal state (e.g., segment reference, current offset) in a null/inconsistent state
  2. Does NOT cause subsequent operations (e.g., getSegment(), getCurrentOffset()) to return null or throw NullPointerException
  3. The segment manager should either recover gracefully or maintain a consistent observable state after the exception

- Include concrete values/examples: For example, if the code calls `segmentBuilder.buildSegment()` which can throw `Exception`, the test should:
  - Mock or simulate a build failure (e.g., using Mockito `when(mockBuilder.buildSegment()).thenThrow(new RuntimeException("build failed"))`)
  - Call the method that triggers the build (e.g., `manager.buildSegmentAndReplace()`)
  - Then verify that manager state methods like `manager.getSegment()` return non-null values, or that no NullPointerException is thrown on subsequent operations

- Common pitfalls to avoid:
  - Testing only that the exception is thrown/logged, without verifying state consistency afterward
  - Assuming that after an exception the segment reference is automatically cleared/reset
  - Not testing with actual null interactions after the exception (e.g., calling `manager.getSegment().getMetadata()` without null-checking)
  - Using overly generic exception types when the actual bug involves a specific checked/unchecked exception (e.g., `IOException` vs `RuntimeException`)
  - Only testing the happy path where build succeeds, missing the exception recovery scenario entirely

- Example of correct test:
```java
@Test
public void testSegmentBuildException() throws Exception {
    // Setup: mock segment builder to throw on build
    when(mockSegmentBuilder.buildSegment()).thenThrow(new RuntimeException("build failed"));
    
    // Act: invoke the method that triggers build
    try {
        manager.buildSegmentAndReplace();
    } catch (RuntimeException e) {
        // expected
    }
    
    // Assert: verify state is not corrupted — getSegment() should NOT return null
    assertNotNull("Segment should not be null after build failure", manager.getSegment());
    
    // Verify subsequent operations don't NPE
    assertNotNull("Segment metadata should be accessible", manager.getSegment().getMetadata());
}
```

- Example of incorrect test (missing state validation):
```java
// WRONG: Only checks exception was thrown, misses state corruption
@Test
public void testSegmentBuildException() {
    assertThrows(RuntimeException.class, () -> manager.buildSegmentAndReplace());
    // Missing: assertNotNull(manager.getSegment())
}
```