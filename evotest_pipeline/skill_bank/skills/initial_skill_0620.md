---
name: proxy-type-unwrapping-for-repository-lookup
description: When looking up repository metadata (bean name, existence check) by domain
  class, the domain class may be a CGLIB/Javassist proxy subclass rather than the
  actual user-defined class. The TG should test that ClassUtils.getUserClass() is
  called to unwrap proxies before repository lookups, otherwise proxy subclasses will
  fail to match.
code_tags:
- TYPE_CONVERSION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# proxy-type-unwrapping-for-repository-lookup

## Instructions

# Proxy Type Unwrapping for Repository Metadata Lookups

## Instructions

- WHEN the TG encounters code that looks up repository metadata (e.g., `repositoryFactoryInfos.containsKey(domainClass)` or `repositoryBeanNames.get(domainClass)`) using a domain class parameter
- THEN the TG should verify that the code first unwraps proxy/AOP-generated subclasses by calling `ClassUtils.getUserClass(domainClass)` BEFORE using the class for map lookups
- Specifically, the TG should test that passing a CGLIB-proxied subclass (e.g., a dynamically generated subclass like `User$$EnhancerByCGLIB$$...`) still correctly finds the repository for the actual user class (e.g., `User.class`)
- The test should:
  1. Create a concrete repository for a known domain class (e.g., `User`)
  2. Obtain a proxied version of that domain class (use any mechanism that generates a subclass proxy, e.g., a simple subclass like `class UserProxy extends User {}`)
  3. Call the method (e.g., `hasRepositoryFor()`, `getRepositoryFor()`) with the proxy class
  4. Assert that the method returns the same result as when called with the original user class (e.g., `assertTrue(repositories.hasRepositoryFor(proxyClass))`)

- Common pitfalls to avoid:
  - Testing only with the exact domain class and not testing with a proxy subclass — the bug only manifests when a proxy subclass is passed
  - Assuming the code works because it works for the exact domain class
  - Using mocks for the proxy class instead of using an actual subclass that extends the domain class

### Correct Example
```java
// Given a repository for User.class
// When querying with a proxy subclass of User
Class<?> proxyClass = new ClassHierarchyBuilder()
    .add(Entity.class, User.class, new UserRepository())
    .getProxyClass(User.class); // returns a subclass like User$$EnhancerByCGLIB$$...

Repositories repositories = new Repositories(...);

// Then the repository should still be found
assertTrue(repositories.hasRepositoryFor(proxyClass));
assertNotNull(repositories.getRepositoryFor(proxyClass));
```

### Incorrect Example (would miss the bug)
```java
// Only testing with the exact class — this passes even with the bug
assertTrue(repositories.hasRepositoryFor(User.class));

// But testing with a proxy class would fail in the buggy version
// assertTrue(repositories.hasRepositoryFor(proxyClass)); // MISSING
```