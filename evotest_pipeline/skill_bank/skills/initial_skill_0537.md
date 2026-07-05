---
name: colocation-constraint-after-restart
description: When testing ExecutionGraph restart with co-located JobVertices sharing
  a SlotSharingGroup, the TG should verify that CoLocationConstraints are properly
  reset and reassigned during restart, not stale from the previous execution.
code_tags:
- VALIDATION
- STATE_MUTATION
- NULL_CHECK
- CO_LOCATION_CONSTRAINT_AFTER_RESTART
test_pattern: STATE_TEST
---

# colocation-constraint-after-restart

## Instructions

# CoLocation Constraint Reset After Restart

## Instructions

- WHEN the TG encounters code that creates an `ExecutionGraph` with `JobVertex` instances that are co-located via `setStrictlyCoLocatedWith()` and belong to the same `SlotSharingGroup`, and the graph is subject to restart via a `RestartStrategy` (e.g., `FixedDelayRestartStrategy(1, 0L)`)
- THEN the TG should write a test that:
  1. Sets up two `JobVertex` instances with parallelism > 1 (e.g., `NUM_TASKS = 31`), both in the same `SlotSharingGroup` and co-located via `vertex1.setStrictlyCoLocatedWith(vertex2)`.
  2. Creates an `ExecutionGraph`, attaches the job graph vertices, and schedules execution.
  3. Triggers a restart using `restartAfterFailure(eg, new FiniteDuration(2, TimeUnit.MINUTES), false)` that simulates a failure and automatic restart of the graph.
  4. After the restart completes and the graph reaches `JobStatus.RUNNING`, validates that for each subtask index `i` (0 to parallelism-1), each `CoLocationConstraint` obtained via `tasks[0].getTaskVertices()[i].getLocationConstraint()` and `tasks[1].getTaskVertices()[i].getLocationConstraint()` is:
     - Not null (i.e., `assertNotNull(constr.getSharedSlot())`)
     - Assigned (i.e., `assertTrue(constr.isAssigned())`)
     - Equal to each other (i.e., `assertEquals(constr1, constr2)`)
  5. Expects that without proper constraint reset during restart, the constraints may retain stale shared slots from the pre-restart execution, causing `isAssigned()` to return false or `getSharedSlot()` to return null, resulting in the graph getting stuck in `FAILING` state instead of `RUNNING`.

- Common pitfalls to avoid:
  - Testing only the first restart attempt without validating the constraints after the graph re-enters `RUNNING` state.
  - Assuming that `CoLocationConstraint` objects are automatically reset or replaced upon restart — they must be explicitly cleared via `CoLocationGroup.resetConstraints()` during the restart process.
  - Using parallelism of 1, which may mask the issue if the constraint reuse logic differs across subtask indices.
  - Not waiting for the graph to reach `RUNNING` state after restart before validating constraints — the expected status after `restartAfterFailure(...)` should be `RUNNING`, not `FAILING`.

- Example correct test pattern:
```java
@Test
public void testConstraintsAfterRestart() throws Exception {
    // Setup
    Instance instance = ExecutionGraphTestUtils.getInstance(
        new ActorTaskManagerGateway(
            new SimpleActorGateway(TestingUtils.directExecutionContext())),
        NUM_TASKS);
    Scheduler scheduler = new Scheduler(TestingUtils.defaultExecutionContext());
    scheduler.newInstanceAvailable(instance);

    JobVertex groupVertex = newJobVertex("Task1", NUM_TASKS, NoOpInvokable.class);
    JobVertex groupVertex2 = newJobVertex("Task2", NUM_TASKS, NoOpInvokable.class);

    SlotSharingGroup sharingGroup = new SlotSharingGroup();
    groupVertex.setSlotSharingGroup(sharingGroup);
    groupVertex2.setSlotSharingGroup(sharingGroup);
    groupVertex.setStrictlyCoLocatedWith(groupVertex2);

    JobGraph jobGraph = new JobGraph("Pointwise job", groupVertex, groupVertex2);
    ExecutionGraph eg = newExecutionGraph(new FixedDelayRestartStrategy(1, 0L), scheduler);
    eg.attachJobGraph(jobGraph.getVerticesSortedTopologicallyFromSources());

    eg.scheduleForExecution();
    assertEquals(JobStatus.RUNNING, eg.getState());

    validateConstraints(eg); // sanity check before restart

    restartAfterFailure(eg, new FiniteDuration(2, TimeUnit.MINUTES), false);

    // After restart, constraints should be reassigned properly
    validateConstraints(eg);

    haltExecution(eg);
}

private void validateConstraints(ExecutionGraph eg) {
    ExecutionJobVertex[] tasks = eg.getAllVertices().values().toArray(new ExecutionJobVertex[2]);
    for (int i = 0; i < NUM_TASKS; i++) {
        CoLocationConstraint constr1 = tasks[0].getTaskVertices()[i].getLocationConstraint();
        CoLocationConstraint constr2 = tasks[1].getTaskVertices()[i].getLocationConstraint();
        assertNotNull(constr1.getSharedSlot());
        assertTrue(constr1.isAssigned());
        assertEquals(constr1, constr2);
    }
}
```

- Example failing test pattern (what NOT to do):
```java
// BAD: Only tests constraints before restart, not after
@Test
public void testCoLocationSetup() throws Exception {
    ExecutionGraph eg = createCoLocatedGraph(NUM_TASKS);
    eg.scheduleForExecution();
    assertEquals(JobStatus.RUNNING, eg.getState());
    // Validates only initial constraints, misses the restart case
    validateConstraints(eg); 
    // No restart triggered — the bug would not be caught
}
```