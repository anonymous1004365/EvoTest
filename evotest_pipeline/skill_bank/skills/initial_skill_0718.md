---
name: case-insensitive-username-lookup
description: When performing user lookup by username, the TG should test that the
  lookup is case-insensitive if the application requires case-insensitive login behavior.
  Many repositories default to case-sensitive matching, which can cause login failures
  for users with uppercase/mixed-case usernames.
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
- CASE_INSENSITIVE_USERNAME_LOOKUP
test_pattern: PARAMETRIC_TEST
---

# case-insensitive-username-lookup

## Instructions

# Case-Insensitive Username Lookup Testing

## Instructions

- WHEN the TG encounters a method that loads/fetches a user by username (e.g., `loadUserByUsername`, `findByUsername`, `findByEmail`), and the system is expected to handle login or user authentication
- THEN the TG should write a test that verifies the lookup is case-insensitive by:
  1. Creating/persisting a user with a username that has a specific case (e.g., `"TestUser"`)
  2. Calling the lookup method with the same username in a **different case** (e.g., `"testuser"` or `"TESTUSER"`)
  3. Verifying that the user is still found successfully (not throwing an exception like `UsernameNotFoundException`)
  4. Verifying the returned user object has the correct username/identifier

- **Common pitfalls:**
  - Testing only with exact-case matches (e.g., looking up `"testuser"` after storing `"testuser"`). This passes even if the lookup is case-sensitive and hides the bug.
  - Testing only one variant of case change — test at least both all-lowercase and all-uppercase variations against a mixed-case stored username.
  - Using a repository/DAO method that defaults to case-sensitive matching (e.g., Spring Data JPA's `findByUsername` without `IgnoreCase` suffix).
  - Forgetting that the lookup might also normalize the username before querying — check whether the system does its own lowercasing.

- **Example (correct test):**
  ```java
  // Given: a user exists with username "TestUser"
  userRepository.save(new User("TestUser", "password"));

  // When: looking up with a different case
  UserDetails user = userDetailsService.loadUserByUsername("testuser");

  // Then: the user should be found
  assertThat(user.getUsername(), is("TestUser"));
  ```

- **Example (incorrect test — misses the bug):**
  ```java
  // This only tests exact-case matching
  userRepository.save(new User("testuser", "password"));
  UserDetails user = userDetailsService.loadUserByUsername("testuser");
  assertNotNull(user);
  // ^ Passes even if the system is case-sensitive!
  ```

- **Expected failure signature on buggy version:**
  The method throws `UsernameNotFoundException` (or equivalent) when the case differs, or returns `null` instead of the user object.