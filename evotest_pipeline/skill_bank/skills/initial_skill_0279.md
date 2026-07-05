---
name: iteration-temp-side-input-handling
description: When generating JobGraph for bulk iterations with temporary side inputs
  (e.g., TempInIterationTest), the JobGraphGenerator must correctly handle the graph
  structure where intermediate results feed into the next iteration. Use this skill
  to write tests that verify no NullPointerException occurs when compiling iterations
  with temporary results.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: EXCEPTION_TEST
---

# iteration-temp-side-input-handling

## Instructions

# Iteration Temp Side Input Handling

## Instructions

- WHEN the TG encounters `JobGraphGenerator` code that compiles bulk iterations (workset/step functions that involve temporary intermediate results) — especially when the optimizer plan contains a `BulkIterationPlanNode` with multiple inputs and intermediate solution set deltas
- THEN the TG should write a test that:
  1. Constructs a complete Flink program with a bulk iteration (e.g., a ConnectedComponents-style or custom iteration using `iterate()` / `iterateDelta()`) where the step function produces a temporary result (e.g., a `GroupReduce`, `Map`, or `Join` transformation) that feeds back into the next iteration
  2. Calls `new JobGraphGenerator().compileJobGraph(...)` on the optimizer plan
  3. Asserts that the method completes without throwing a `NullPointerException` — this catches the bug where the generator traverses side-input graphs without properly initializing/handling the connection
- Do NOT assume the test must check specific job graph vertices or edges — the bug manifests as a `NullPointerException` during graph compilation, so the test should verify exception-free execution
- Include the `TempInIterationsTest` pattern as a reference: set up the Flink program with `ExecutionEnvironment`, add a `BulkIteration` with a step function that chains `.map()` / `.groupBy().reduce()` / `.withParameters(...)` operations, then verify the compiled job graph output is non-null
- Common mistake: testing only simple iterations without temporary/side-input chains, or testing only the final result without compiling the job graph — both of which would miss the NPE in graph traversal

### Correct Example
```java
public class IterationWithTempTest {
    @Test
    public void testTempInIterationTest() {
        ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();
        DataSet<Long> input = env.generateSequence(1, 100);
        
        // Create a bulk iteration with a temp result in the step function
        IterativeDataSet<Long> iteration = input.iterate(10);
        DataSet<Long> step = iteration.map(new MapFunction<Long, Long>() {
            @Override
            public Long map(Long value) { return value * 2; }
        });
        DataSet<Long> result = iteration.closeWith(step);
        
        // Compile the job graph — this is where the NPE would occur
        Plan plan = env.createProgramPlan();
        JobGraphGenerator generator = new JobGraphGenerator();
        JobGraph jobGraph = generator.compileJobGraph(plan);
        
        // Verify no exception and output is produced
        assertNotNull(jobGraph);
    }
}
```