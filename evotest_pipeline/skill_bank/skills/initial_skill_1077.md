---
name: versionless-dependency-validation
description: When validating Maven project model dependencies, ensure both direct
  dependencies and managed dependencies have non-null versions. Missing versions cause
  InvalidArtifactRT failures downstream. This skill teaches how to write tests that
  catch unversioned dependency declarations in POM files.
code_tags:
- VALIDATION
- VERSIONLESS_DEPENDENCY_VALIDATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# versionless-dependency-validation

## Instructions

# Versionless Dependency Validation

## Instructions

**WHEN** the TG encounters a Maven project model building or POM parsing code path that processes `<dependency>` or `<dependencyManagement>` entries:

- **THEN** write a test that declares a dependency **without a `<version>` element** in both the `<dependencies>` section and the `<dependencyManagement>` section of a test POM file
- **THEN** build the project model using `ProjectBuilder.build()` with that POM
- **THEN** verify that the build throws `InvalidArtifactRT` (or `InvalidArtifactRT` subclass), because a dependency without a version is invalid and should not be silently accepted
- **THEN** ensure the test POM has:
  - A `<groupId>`, `<artifactId>`, and `<version>` for the project itself
  - A `<dependency>` entry with only `<groupId>` and `<artifactId>` (no `<version>`)
  - A `<dependencyManagement>` entry with only `<groupId>` and `<artifactId>` (no `<version>`) for the same dependency
- **THEN** verify the exception is thrown at build time, not at some later resolution phase

**Common pitfalls to avoid:**

- ❌ Testing only a direct dependency without version, but omitting the `dependencyManagement` entry — the bug was in the managed path too
- ❌ Testing only `dependencyManagement` without a `<dependency>` section — both are needed to trigger the bug
- ❌ Adding a `<scope>` or `<type>` without `<version>` — the missing version is the root cause; extra elements don't change it
- ❌ Using a test POM with valid versions and expecting success — the test must trigger the INVALID case
- ❌ Catching `Exception` too broadly — assert specifically for `InvalidArtifactRT` or a descriptive failure message mentioning artifact resolution

**Correct example:**

```java
@Test
public void testVersionlessManagedDependency() throws Exception {
    File pom = getTestFile("src/test/resources/projects/versionless-managed-dependency.xml");
    assertThrows(InvalidArtifactRT.class, () -> lookup(ProjectBuilder.class).build(pom));
}
```

With `versionless-managed-dependency.xml`:
```xml
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>test</groupId>
  <artifactId>versionless-managed-dependency</artifactId>
  <version>0.0.1-SNAPSHOT</version>
  <dependencies>
    <dependency>
      <groupId>org.apache.maven.its</groupId>
      <artifactId>a</artifactId>
    </dependency>
  </dependencies>
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.apache.maven.its</groupId>
        <artifactId>a</artifactId>
      </dependency>
    </dependencies>
  </dependencyManagement>
</project>
```

**Incorrect example (won't catch the bug):**

```java
// Only tests direct dependency, no dependencyManagement — misses the bug path
@Test
public void testVersionlessDependency() throws Exception {
    File pom = getTestFile("src/test/resources/projects/versionless-dependency.xml");
    // If only direct dependency misses version, it might be handled differently than managed
    lookup(ProjectBuilder.class).build(pom); // silently succeeds
}
```