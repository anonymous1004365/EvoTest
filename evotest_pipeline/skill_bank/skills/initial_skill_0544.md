---
name: clone-method-deep-copy-collection-fields
description: When a class implements Cloneable and has mutable collection fields (e.g.,
  List<Profile>), the clone() or deepCopy() method must create new collection instances,
  not just assign the same reference. This skill teaches how to test for proper deep
  copying of collection fields during cloning.
code_tags:
- STATE_MUTATION
- NULL_CHECK
- COLLECTION_SHALLOW_CLONE
test_pattern: STATE_TEST
---

# clone-method-deep-copy-collection-fields

## Instructions

# Cloned Object Collection Fields Must Be Independent Copies

## Instructions

- WHEN the TG encounters a class that implements `Cloneable` and has a `clone()` method that calls a `deepCopy()` method (like `MavenProject.clone()` calling `deepCopy(MavenProject)`), and that class has mutable List, Set, or Map fields (e.g., `List<Profile> activeProfiles`)
- THEN the TG should verify that after cloning, modifying the collection obtained from the clone does NOT affect the original object's collection (and vice versa). The test should:
  1. Create an original object and populate a mutable collection field (e.g., add a `Profile` to `activeProfiles`)
  2. Clone the object (e.g., `original.clone()`)
  3. Get the collection from both original and clone (e.g., `getActiveProfiles()`)
  4. Assert that the two collection references are NOT the same object using `assertNotSame()`
  5. Optionally assert that the collections have the same elements (same size, same content)
  6. Optionally mutate one collection (e.g., add/remove an element) and assert the other collection remains unchanged

- WHEN testing collection deep-copy in clone methods, be careful to test with NON-EMPTY collections. If the collection is empty, a shallow copy might appear to work because both hold empty lists, but the bug only manifests when elements are added later.
- Common pitfall: Only checking that `getActiveProfiles()` returns a non-null list or returns the same number of elements, without verifying that the references are distinct. The bug is that `activeProfiles` is assigned directly (`this.activeProfiles = project.activeProfiles`) instead of creating a new `ArrayList<>(project.activeProfiles)`.
- Common pitfall: Testing with only one collection field when the class has multiple collection fields that might all be shallow-copied.
- Use `assertNotSame()` on the collection references (not just `assertEquals()` or `assertNotNull()`).

### Example (correct)

```java
File f = getFileForClasspathResource("withActiveByDefaultProfile-pom.xml");
MavenProject projectToClone = getProject(f);
List<Profile> activeProfilesOrig = projectToClone.getActiveProfiles();

assertEquals("Expecting 1 active profile", 1, activeProfilesOrig.size());

MavenProject clonedProject = projectToClone.clone();

List<Profile> activeProfilesClone = clonedProject.getActiveProfiles();

assertEquals("Expecting 1 active profile", 1, activeProfilesClone.size());

// CRITICAL: verify the lists are different objects (deep copy)
assertNotSame("The list of active profiles should have been cloned too but is same",
              activeProfilesOrig, activeProfilesClone);
```

### Example (incorrect — missing assertNotSame)

```java
MavenProject clonedProject = projectToClone.clone();
List<Profile> activeProfilesClone = clonedProject.getActiveProfiles();

// BAD: Only checks size/content, doesn't verify reference independence
assertEquals(1, activeProfilesClone.size());
// Missing: assertNotSame(activeProfilesOrig, activeProfilesClone);
// With shallow copy, adding a profile to one list would affect the other!
```