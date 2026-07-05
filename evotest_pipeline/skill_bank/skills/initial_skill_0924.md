---
name: partition-release-with-spill-index-boundary
description: When testing partition views that can be released and re-read after spilling,
  the TG must test that reading from the next buffer index after release does not
  throw IndexOutOfBoundsException. The view operates with a spill file and a current
  buffer index that may shift during spilling.
code_tags:
- BOUNDARY_CHECK
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# partition-release-with-spill-index-boundary

## Instructions

# Partition Release With Spill Index Boundary

## Instructions

- WHEN the TG encounters a `ResultSubpartitionView` (e.g., `SpillableSubpartitionView`, `SpilledSubpartitionView`) that has an internal buffer index tracking which buffer to read next, and the view's backing partition can be released (e.g., `releasePartition` is called on the partition), and the view has a method like `getNext()` or `getNextBuffer()` that reads the buffer at the current index:
  
  THEN the TG should write a test that:
  1. Adds at least one buffer to the partition (e.g., via `addBuffer`), so the view has data to read.
  2. Creates a view from the partition (e.g., `subpartition.createReadableView(...)`).
  3. Reads from the view (e.g., `view.getNextBuffer()`) to advance past the first buffer.
  4. **Calls `releasePartition()` or equivalent** on the partition to trigger spilling/state mutation.
  5. After release/spilling, calls `view.getNextBuffer()` again (or the equivalent method for getting the next item) and verifies it does **not** throw `IndexOutOfBoundsException`.
  6. The expected behavior after release is that the view should either return the next buffer successfully, or return `null`/`BufferAvailabilityEvent` indicating no more data — but never throw an `IndexOutOfBoundsException`.

- WHEN the internal buffer index is used to track which buffer in a list/array to read next, and spilling (triggered by `releasePartition`, `spillPartition`, or similar) changes the internal state of the buffer tracking:
  
  THEN the TG must test the sequence: add buffer → read buffer → spill/release → read again, and verify no index exception occurs. The bug occurs when the view's internal index (e.g., `currentIndex`, `nextBufferToRead`) is not properly adjusted or reset after the spilling operation mutates the underlying buffer storage.

- Common pitfalls:
  - Testing only the happy path where all buffers are read before release.
  - Testing only the case where `releasePartition` is called before any reads.
  - Not verifying that `getNextBuffer()` works after `releasePartition()` when some buffers were already consumed.
  - Not using the specific exception class (`IndexOutOfBoundsException`) as the error to expect (and catch, verifying it does NOT occur).

- **Correct example** (conceptual):
  ```java
  @Test
  public void testReleasePartitionAndGetNext() throws Exception {
      SpillableSubpartition subpartition = ...;
      subpartition.addBuffer(...); // add a buffer
      SpillableSubpartitionView view = subpartition.createReadableView(...);
      
      // consume first buffer
      view.getNextBuffer(); // should be OK
      
      // trigger spilling which mutates internal index state
      subpartition.releasePartition();
      
      // this should NOT throw IndexOutOfBoundsException
      assertNull(view.getNextBuffer());
  }
  ```

- **Incorrect example** (missing the release-and-read sequence):
  ```java
  @Test
  public void testGetNextAfterRelease() throws Exception {
      SpillableSubpartition subpartition = ...;
      SpillableSubpartitionView view = subpartition.createReadableView(...);
      
      // Only testing release BEFORE any reads
      subpartition.releasePartition();
      
      // This path works but doesn't expose the index bug
      assertNull(view.getNextBuffer());
  }
  ```