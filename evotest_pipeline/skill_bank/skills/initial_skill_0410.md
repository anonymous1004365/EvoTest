---
name: dependency-graph-cycle-error-storage
description: WHEN building a project dependency graph produces a cycle error, THEN
  the test should verify that the cycle exception is properly stored in the MavenExecutionResult
  and is accessible via getExceptions(). This skill applies to testing robustness
  of project dependency graph construction when modules have circular inter-dependencies.
code_tags:
- DEPENDENCY_GRAPH_CYCLE
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# dependency-graph-cycle-error-storage

## Instructions

# Dependency Graph Cycle Error Storage

## Instructions

**WHEN** the TG encounters a call to `buildGraph(MavenSession, MavenExecutionResult)` that constructs a `ProjectDependencyGraph` from project modules which may have cyclic inter-dependencies (e.g., module-a depends on module-b and module-b depends on module-a):

- **THEN** the TG should create a multi-module test project with a **direct cyclic dependency** between modules (e.g., module-a has a `<dependency>` on module-b, and module-b has a `<dependency>` on module-a), using a parent POM with `<packaging>pom</packaging>` and both modules declared in `<modules>`.

- **THEN** the TG should execute `Maven.execute(Iterable, MavenExecutionRequest)` (or the equivalent entry point) on this cyclic project and capture the `MavenExecutionResult` object.

- **THEN** the TG should verify that the result's `getExceptions()` list is **not empty** and that the first exception (`getExceptions().get(0)`) is of type `org.apache.maven.ProjectCycleException`.

- **THEN** the test should use `assertEquals(ProjectCycleException.class, result.getExceptions().get(0).getClass())` (with the appropriate static import) to assert the exact exception type.

- **Common mistakes to avoid:**
  - **Do NOT** test only linear or tree-shaped dependency graphs — the bug only manifests with actual cycles.
  - **Do NOT** test cycle detection without verifying the exception is stored in `getExceptions()` — the bug was that the cycle exception might not be propagated correctly.
  - **Do NOT** mock `GraphBuilder` or `ProjectDependencyGraph` — this test requires a real multi-module build with real POM files on disk.
  - **Do NOT** forget to set up the multi-module project directory structure under the test resources directory (e.g., `src/test/projects/default-maven/cyclic-reference/`).

- **Correct example (pseudo-code):**
  ```java
  @Test
  public void testThatErrorDuringProjectDependencyGraphCreationAreStored() throws Exception {
      // Given: a multi-module project with cyclic dependencies
      File basedir = new File("src/test/projects/default-maven/cyclic-reference");
      MavenExecutionRequest request = new DefaultMavenExecutionRequest();
      request.setBaseDirectory(basedir);
      request.setPom(new File(basedir, "pom.xml"));

      // When: executing Maven
      MavenExecutionResult result = maven.execute(ImmutableList.of(request.getProject()), request);
      
      // Then: the cycle exception should be stored
      assertFalse(result.getExceptions().isEmpty());
      assertEquals(ProjectCycleException.class, result.getExceptions().get(0).getClass());
  }
  ```

- **Incorrect example:**
  ```java
  @Test
  public void testCycleDetection() {
      // WRONG: Mocking the graph builder won't catch the real bug
      GraphBuilder builder = mock(GraphBuilder.class);
      when(builder.buildGraph(any(), any())).thenThrow(new ProjectCycleException("cycle"));
      // This test passes even with the buggy version because it doesn't test
      // the real integration path through DefaultMaven.doExecute()
  }
  ```