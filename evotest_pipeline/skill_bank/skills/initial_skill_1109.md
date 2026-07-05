---
name: downstream-upstream-projects-sorted-order
description: Teaches the TG to verify that getDownstreamProjects and getUpstreamProjects
  return projects in topological (sorted) order, not in insertion order. Use when
  testing DependencyGraph implementations that delegate to ProjectSorter or any topological
  sorter.
code_tags:
- ORDER_DEPENDENCY
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# downstream-upstream-projects-sorted-order

## Instructions

# Downstream/Upstream Projects Must Return Sorted Order

## Instructions

- WHEN the TG encounters a `ProjectDependencyGraph` implementation (like `DefaultProjectDependencyGraph`) that wraps a `ProjectSorter` topological sorter, and the code under test calls `getDownstreamProjects(project, transitive)` or `getUpstreamProjects(project, transitive)`
- THEN the TG MUST verify that the returned list respects the topological sort order, not the order in which projects were added to the graph. Specifically, construct multiple projects (e.g., 4+ projects) all depending on the same root project, add them to the graph in an order that differs from the topological order (e.g., [depender1, depender2, depender3, aProject] where aProject is the root), then call `getDownstreamProjects(aProject, true)` and assert that each element matches the expected sorted order (e.g., depender1 at index 0, depender2 at index 1, depender3 at index 2)
- WHEN the TG tests `getDownstreamProjects` with `transitive=false`
- THEN it MUST verify that only direct downstream projects are returned, but still in sorted topological order (e.g., if depender4 depends on depender3 which depends on aProject, depender4 should NOT appear when transitive=false, but depender3 should appear before other direct dependents in sorted order)
- WHEN the TG tests `getUpstreamProjects` with `transitive=true`
- THEN it MUST verify that upstream projects are returned in sorted topological order (e.g., for depender1 that depends on aProject, the list should contain aProject)
- Include concrete values, types, and method names from the actual code: use `MavenProject`, `DefaultProjectDependencyGraph`, `Arrays.asList(...)`, `ProjectSorter.getId(project)`, and the `Dependency` model class
- Common pitfall: testing `getDownstreamProjects` only with 2 projects (root + 1 depender) which passes even if order is insertion-based. Use at least 3+ dependers that all have the same root to catch the bug
- Common pitfall: adding projects in the same order as topological order — the test MUST use an insertion order that differs from topological sorted order to expose the bug
- Common pitfall: forgetting to set groupId, artifactId, and version on MavenProject instances, which are required for ProjectSorter.getId() to work
- Common pitfall: only testing `getSortedProjects()` which delegates to `ProjectSorter.getSortedProjects()` — the bug is specifically in the `getDownstreamProjects`/`getUpstreamProjects` methods which build a Set from the recursive traversal and then resolve back to sorted order

### Example (Correct)

```java
// Creates 3 dependers all depending on a single root project 'aProject'
// IMPORTANT: Add to graph in order [depender1, depender2, depender3, aProject]
// which differs from topological order [aProject, depender1, depender2, depender3]
MavenProject aProject = createA();
MavenProject depender1 = createProject(Arrays.asList(toDependency(aProject)), "depender1");
MavenProject depender2 = createProject(Arrays.asList(toDependency(aProject)), "depender2");
MavenProject depender3 = createProject(Arrays.asList(toDependency(aProject)), "depender3");

ProjectDependencyGraph graph = new DefaultProjectDependencyGraph(
    Arrays.asList(depender1, depender2, depender3, aProject));

// This is the key assertion that catches the bug:
// Downstream projects must be returned in topological order, not insertion order
List<MavenProject> downstreamProjects = graph.getDownstreamProjects(aProject, true);
assertEquals(depender1, downstreamProjects.get(0));
assertEquals(depender2, downstreamProjects.get(1));
assertEquals(depender3, downstreamProjects.get(2));
```

### Example (Incorrect)

```java
// WRONG: Only testing with 2 projects — cannot detect order bug
MavenProject aProject = createA();
MavenProject depender = createProject(Arrays.asList(toDependency(aProject)), "depender");
ProjectDependencyGraph graph = new DefaultProjectDependencyGraph(Arrays.asList(depender, aProject));
List<MavenProject> downstream = graph.getDownstreamProjects(aProject, true);
assertEquals(1, downstream.size()); // passes even with buggy code!

// WRONG: Adding in topological order — insertion order matches, bug hidden
ProjectDependencyGraph graph = new DefaultProjectDependencyGraph(
    Arrays.asList(aProject, depender1, depender2, depender3));
// Order happens to be correct by coincidence — bug not exposed

// WRONG: Forgetting that sort order is topological, not alphabetical or by field
```