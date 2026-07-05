---
name: pending-event-queue-for-uninitialized-channels
description: When a reader has uninitialized (UnknownInputChannel) channels, events
  sent backwards before all channels are resolved must be queued/pending rather than
  immediately dispatched, otherwise events to uninitialized channels are silently
  lost. Use this skill when testing components that send events through readers with
  mixed initialized/uninitialized channel sets.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- PENDING_QUEUE_UNINITIALIZED_CHANNEL
test_pattern: STATE_TEST
---

# pending-event-queue-for-uninitialized-channels

## Instructions

# Pending Event Queue for Uninitialized Channels

## Instructions

WHEN the TG encounters a system where a reader (e.g., `BufferReader`) holds a mix of initialized channels and uninitialized `UnknownInputChannel` instances, and the system sends events backwards (e.g., `sendTaskEvent(TaskEvent)`), THEN the TG should test that events sent before all channels are initialized are not lost but instead queued and delivered once the uninitialized channels are resolved.

Specifically:
- WHEN a reader has some `LocalInputChannel` and some `UnknownInputChannel` channels registered via `setInputChannel()`, and only the initialized channels have been requested (via `requestPartitionsOnce()`)
- WHEN a `TaskEvent` is sent backwards via `reader.sendTaskEvent(event)` before the unknown channels are updated (via `updateInputChannel(PartitionInfo)`)
- THEN the test should verify that the event is delivered to ALL channels (both the originally initialized ones AND the ones that were uninitialized at send time) after the unknown channels are resolved.

To test this:
1. Create a reader with at least one `LocalInputChannel` and at least one `UnknownInputChannel`.
2. Call `reader.requestPartitionsOnce()` — this only requests partitions for initialized channels.
3. Send a `TaskEvent` via `reader.sendTaskEvent(event)` — on the buggy version, this only delivers the event to already-initialized channels.
4. Call `updateInputChannel(PartitionInfo)` on the reader to resolve the `UnknownInputChannel` into a concrete channel.
5. On the fixed version, the event should also be delivered to the newly-resolved channel. On the buggy version, the event is lost.

Common pitfalls to avoid:
- Testing only with all channels initialized before sending events — this masks the bug.
- Only verifying that the first channel receives the event, without checking that the uninitialized channel also receives it after resolution.
- Not waiting for `updateInputChannel()` to be called after `sendTaskEvent()` before verifying event delivery.

Example of a correct test:

```java
// Setup reader with 1 local + 1 unknown channel
BufferReader reader = new BufferReader(mock(RuntimeEnvironment.class), networkEnvironment, resultId, 2, 0);
reader.setBufferPool(bufferPool);

InputChannel local = new LocalInputChannel(0, localProducer, localPartitionId, reader);
InputChannel unknown = new UnknownInputChannel(1, unknownProducer, unknownPartitionId, reader);
reader.setInputChannel(localPartitionId, local);
reader.setInputChannel(unknownPartitionId, unknown);

reader.requestPartitionsOnce();

// Send event BEFORE unknown channel is resolved — bug: event lost for unknown channel
reader.sendTaskEvent(new TestTaskEvent());

// Now resolve the unknown channel
PartitionInfo partitionInfo = new PartitionInfo(unknownPartitionId, PartitionLocation.LOCAL, null);
reader.updateInputChannel(partitionInfo);

// Verify: event was sent to both channels (local channel directly, unknown after resolution)
// On fixed version: taskEventDispatcher.publish() was called 2 times
verify(taskEventDispatcher, times(2)).publish(any(ExecutionAttemptID.class), any(IntermediateResultPartitionID.class), any(TaskEvent.class));
```

Example of an incorrect test (does NOT catch this bug):

```java
// ❌ BAD: Resolves unknown channel BEFORE sending event
reader.requestPartitionsOnce();
PartitionInfo partitionInfo = ...;
reader.updateInputChannel(partitionInfo);  // resolve first
reader.sendTaskEvent(event);               // then send — both channels are initialized, no bug triggered
verify(taskEventDispatcher, times(2)).publish(...);
```