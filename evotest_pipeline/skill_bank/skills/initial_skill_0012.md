---
name: spillable-subpartition-view-release
description: When a SpillableSubpartition view is created via readView and then the
  parent partition is released, any resources held by the view (e.g., file channels)
  must also be properly released. Use this skill when testing that releasing a parent
  SpillableSubpartition correctly triggers view cleanup, preventing resource leaks
  or incomplete view state transitions.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- RESOURCE_MANAGEMENT
- STATE_MUTATION
test_pattern: STATE_TEST
---

# spillable-subpartition-view-release

## Instructions

# SpillableSubpartition View Release After Parent Partition Release

## Instructions

- WHEN the TG encounters a `SpillableSubpartition` that creates a view via `readView()` (returning a `SpillableSubpartitionView`) AND the view acquires resources (e.g., a `FileChannel` from spilling),

- THEN the TG should test that releasing the parent partition (e.g., `partition.release()`) properly propagates to the view, ensuring the view's resource is released and its internal state transitions to "released."

  - **How to test**:  
    1. Create a `SpillableSubpartition` (from a `ResultPartition`) and add at least one buffer to it.  
    2. Call `readView()` to obtain the `ResultSubpartitionView`.  
    3. Call `release()` on the parent partition (NOT on the view directly).  
    4. Verify the view's state: call `view.isReleased()` — it should return `true`.  
    5. Verify the view's `getNextBuffer()` returns `null` or throws an appropriate exception (e.g., `IllegalStateException` with message indicating the view is released).  
    6. Also verify that any underlying resource (e.g., `FileChannel`) held by the view is closed — check via `view.isReleased()` or by inspecting the channel state if accessible.

- **Common pitfalls to avoid**:
  - Do NOT assume that releasing the partition leaves the view unaffected — the bug is exactly that the view was not released when the parent was released.
  - Do NOT test only `partition.isReleased()` — you must check the **view's** released state.
  - Do NOT forget to add at least one buffer to the partition before calling `readView()`, otherwise the view may not acquire the resource (e.g., no spilling occurs).
  - Do NOT skip `partition.release()` and go directly to `view.releaseAllResources()` — the bug is specifically about the partition release path not cleaning up views.

- **Example (correct test approach)**:
  ```java
  // Setup
  ResultPartition partition = ...; // with SpillableSubpartition
  partition.addBuffer(buffer, 0);
  ResultSubpartitionView view = partition.readView(0);
  
  // Release the parent partition
  partition.release();
  
  // Verify the view is released
  assertTrue("View should be released after partition release", view.isReleased());
  assertNull("View should return null after release", view.getNextBuffer());
  ```

- **Incorrect approach (would miss the bug)**:
  ```java
  // Only releases the view directly, not testing partition release path
  partition.readView(0);
  view.releaseAllResources();
  assertTrue(view.isReleased()); // This passes even on buggy code
  ```