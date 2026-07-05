---
name: barrier-buffer-cleanup-on-cancellation
description: When testing barrier/temporary buffer implementations with checkpoint
  alignment, verify that temporary files are cleaned up when a cancellation barrier
  arrives before all aligned barriers. Tests should simulate multi-channel scenarios
  where an earlier checkpoint is cancelled during alignment and verify no temp files
  remain.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# barrier-buffer-cleanup-on-cancellation

## Instructions

# Barrier Buffer Cleanup on Cancellation During Alignment

## Instructions

**WHEN** the TG encounters code that manages temporary buffer files during checkpoint barrier alignment (e.g., `BarrierBuffer`, `BufferSpiller`), specifically where barriers are aligned across multiple input channels and temp files are written to disk:

- **THEN** the TG should write a test that:
  1. Creates a multi-channel setup (e.g., 3+ input channels) where not all channels have received their barrier for a given checkpoint ID.
  2. Sends a cancellation barrier (e.g., `CancelCheckpointMarker`) for a **different** checkpoint ID on one of the channels that has NOT yet received the current checkpoint's barrier.
  3. After cancellation, continues sending more data on all channels and then closes them.
  4. After cleanup/close, verifies that **no temporary files remain** on the filesystem (e.g., call a helper method like `checkNoTempFilesRemain()` that lists the spill directory).

- **Key verification**: The test must assert that `currentBuffered.cleanup()` (or equivalent) was invoked during cancellation, such that temporary spill files from the aborted checkpoint alignment are deleted. The failure mode is that temp files silently leak on disk when a cancellation barrier arrives during active alignment.

- **Common pitfalls to avoid**:
  - ❌ Testing only a single channel — the bug only manifests with multiple channels where alignment is in progress.
  - ❌ Sending the cancellation barrier for the **same** checkpoint ID that is being aligned — the bug is triggered when cancellation is for a **different** checkpoint (jumping over).
  - ❌ Not simulating the "jumping over" scenario where a later checkpoint's cancellation arrives while an earlier checkpoint's barriers are partially collected.
  - ❌ Not checking for temp file leaks after cleanup — the test must explicitly verify filesystem state, not just that no exception was thrown.

- **Example (correct)**:
```java
// Setup: 3 input channels, create BarrierBuffer
// Send barrier for checkpoint 1 on channels 0 and 1 (not yet aligned, missing channel 2)
// Send cancellation for checkpoint 2 on channel 2 (jumps over checkpoint 1)
// Send remaining data and end-of-stream markers on all channels
// Cleanup the barrier buffer
// Assert: no temp files remain in spilling directory
```

- **Example (incorrect)**:
```java
// ❌ Wrong: Sends cancellation for same checkpoint, or single-channel test
// Sends barrier for checkpoint 1 on channel 0 only
// Sends cancellation for checkpoint 1 on channel 0
// This does NOT trigger the temp file leak bug
```