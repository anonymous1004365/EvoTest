---
name: optional-dependency-root-ancestry
description: When collecting dependencies where optional artifacts are filtered based
  on ancestry, test that optional artifacts directly under the root node are included.
  The TG should test with dependency trees where an optional artifact is a child of
  the root node.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# optional-dependency-root-ancestry

## Instructions

# Optional Dependency Root Ancestry Test

## Instructions

WHEN the TG encounters code that collects or resolves dependencies and filters out optional artifacts based on whether they are children of the root node (e.g., `node.isChildOfRootNode()` or similar ancestry checks):

- THEN the TG should build a dependency tree where:
  - The root artifact (e.g., `test:a:jar:1.0`) has a direct dependency `test:b:jar:1.0` which declares `test:c:jar:1.0` as an optional dependency.
  - Alternatively, the root has a direct optional dependency directly under it.
- THEN the TG should verify that when an artifact is **both** optional AND a direct child of the root node, it IS still included in the resolved dependency list.
- THEN verify the collected artifact list contains the optional root-child artifact (e.g., assert that `test:b:jar:1.0` is present when it is both optional and a child of the root).
- Include at least one test case where an optional artifact is NOT a direct root child (is deeper in the tree) and verify it IS excluded.

Common pitfalls to avoid:
- Testing only with optional artifacts at non-root levels (which are correctly excluded) without testing the edge case where they are root children.
- Assuming that "optional" always means "excluded" regardless of position in the dependency tree.
- Not constructing a tree deep enough — you need at least root → child (optional) to test the root-child path, or root → intermediate → optional to test the non-root-child path.

Example correct test structure:

```java
// Correct: Test that optional artifact at root child level IS included
Artifact a = new DefaultArtifact("test", "a", "1.0", ...);
Artifact b = new DefaultArtifact("test", "b", "1.0", ...);
// b is optional AND a child of root
// ... build tree with a -> b (optional)
List<Artifact> collected = collector.collect(...);
assertTrue("Optional artifact at root level should be included", 
    collected.contains(b));
```

Example incorrect approach:

```java
// WRONG: Only testing optional at depth > 1
// This would pass even with the bug
Artifact c = new DefaultArtifact("test", "c", "1.0", ...);
// c is optional AND child of intermediate node, NOT root
// ... build tree with a -> b -> c (optional)
List<Artifact> collected = collector.collect(...);
assertFalse("Optional non-root-child artifact should be excluded", 
    collected.contains(c));
// This test would NOT catch the bug because the bug is about root children
```