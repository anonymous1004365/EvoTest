---
name: message-boundary-event-type-validation
description: When testing message boundary events on user tasks, verify that subscriptions
  are correctly created and cancelled across all supported message types (both String
  names and CtTypeReference types). Test with different message types to catch type-handling
  bugs in event subscription logic.
code_tags:
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# message-boundary-event-type-validation

## Instructions

# Message Boundary Event Type Validation

## Instructions

- WHEN a test involves message boundary events on user tasks (e.g., BPMN processes where a message event is attached as a boundary event to a user task node), THEN the test should verify that message subscriptions are correctly created and cancelled when the user task completes, with proper event registration and cleanup.

- WHEN testing message boundary event subscription behavior, THEN test with multiple message type variants — specifically use both `String` message names (e.g., `"Test Message"`) and `CtTypeReference` typed message definitions — to ensure the subscription logic handles different parameter types correctly.

- WHEN a message boundary event is attached to a user task that completes normally (i.e., the boundary event is NOT triggered, the task completes via `taskService.complete()`), THEN verify that all message subscriptions are properly cancelled/removed after task completion, and that the process instance reaches the expected end state.

- Common mistakes to avoid:
    - Only testing with one message type (e.g., only `String` names) when the code supports a union type of `String` or `CtTypeReference` — this misses bugs where one type path is broken.
    - Assuming message subscriptions are always cleaned up on task completion without verifying explicitly that no leftover subscriptions exist.
    - Forgetting to verify both the "boundary event NOT triggered" case and the "boundary event IS triggered" case — the cleanup logic on normal completion is distinct from trigger logic.

### Correct Example (covers both message types, verifies state):

```java
@Test
@Deployment(resources = {"org/activiti/engine/test/bpmn/event/message/MessageBoundaryEventTest.testMessageOnUserTask.bpmn20.xml"})
public void testMessageOnUserTask() {
    // Given: deploy process with message boundary event on user task
    // When: start process instance and wait for user task
    ProcessInstance processInstance = runtimeService.startProcessInstanceByKey("messageBoundaryEventOnUserTask");
    Task userTask = taskService.createTaskQuery().processInstanceId(processInstance.getId()).singleResult();
    assertNotNull(userTask);
    
    // When: complete the user task without triggering the boundary event
    taskService.complete(userTask.getId());
    
    // Then: the process instance should be completed normally
    assertProcessEnded(processInstance.getId());
    // And: message subscriptions should be cleaned up (no active executions on message events)
    assertEquals(0, runtimeService.createExecutionQuery().messageEventSubscriptionName("Test Message").count());
    // Also test with CtTypeReference type if code supports it
    assertEquals(0, runtimeService.createExecutionQuery().messageEventSubscriptionName("typed-message").count());
}
```

### Incorrect Example (only tests one message type, does not verify cleanup):

```java
@Test
@Deployment(resources = {"org/activiti/engine/test/bpmn/event/message/MessageBoundaryEventTest.testMessageOnUserTask.bpmn20.xml"})
public void testMessageOnUserTask() {
    // BAD: Only tests String message type, no verification of subscription cleanup
    ProcessInstance processInstance = runtimeService.startProcessInstanceByKey("messageBoundaryEventOnUserTask");
    Task userTask = taskService.createTaskQuery().processInstanceId(processInstance.getId()).singleResult();
    taskService.complete(userTask.getId());
    // Missing: verify subscription counts for BOTH message types
    // Missing: verify processInstance is ended
}
```