---
name: token-login-module-shared-state-initialization
description: When a login module depends on shared state populated by preceding JAAS
  login modules, the test must verify that shared state values (like userId) are correctly
  retrieved after login. This skill applies to JAAS login module testing where modules
  compose via shared state.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# token-login-module-shared-state-initialization

## Instructions

# Token Login Module Shared State Initialization

## Instructions

- WHEN the TG encounters a test that exercises a JAAS `LoginModule` whose `login()` or `commit()` methods read shared state from the `sharedState` map (e.g., `sharedState.get("javax.security.auth.login.name")`) — AND this shared state is populated by a *different* `LoginModule` that runs first in the login stack
- THEN the TG MUST write a test that:
  1. Creates a `LoginContext` with a `Configuration` object that includes **both** the shared-state-providing module (e.g., `LoginModuleImpl`) and the shared-state-consuming module (e.g., `TokenLoginModule`) in the correct order
  2. Calls `login()` followed by `logout()` on the `LoginContext` to exercise the full lifecycle
  3. After logout, verifies that a **second `login()` call** still works correctly (i.e., the shared state is re-populated and the consuming module can re-read it)
  4. Specifically asserts that after the second login, the user principal ID matches the expected value (e.g., `"admin"` rather than `null`)
- The test must verify that the shared state entry (e.g., `"javax.security.auth.login.name"`) is **not null** and correctly populated after `login()` completes — and that after `logout()` + `login()`, the state is re-initialized properly rather than stale.

- **Common pitfalls to avoid:**
  - Testing only a single login module in isolation without composing modules that populate shared state
  - Testing only one login/logout cycle without verifying re-initialization on a subsequent login
  - Assuming that `commit()` or `logout()` resets internal state in a way that prevents re-login
  - Testing `login()` without also calling `commit()` and `logout()` (which trigger state cleanup)
  - Using a `Configuration` that only includes the consuming module — the test will fail because shared state is never populated

- **Example of a correct test** (grokked from the actual triggering test):
  ```java
  @Test
  public void testTokenAuthInfo() throws Exception {
      Configuration config = ConfigurationUtil.getJackrabbit2Configuration(tokenConfig);
      LoginContext loginCtx = new LoginContext("jackrabbit.oak", null, callbackHandler, config);
      
      // First login
      loginCtx.login();
      Subject subject = loginCtx.getSubject();
      loginCtx.logout();
      
      // Second login — this is where the bug manifests
      loginCtx.login();
      subject = loginCtx.getSubject();
      for (Principal p : subject.getPrincipals()) {
          if (p instanceof TokenDefaultLoginModuleTest.TestTokenAuthInfo) {
              String userId = ((TokenDefaultLoginModuleTest.TestTokenAuthInfo) p).getUserId();
              assertEquals("admin", userId);  // buggy: userId is null on second login
          }
      }
  }
  ```

- **Example of an incorrect test** (would miss the bug):
  ```java
  @Test
  public void testLoginOnce() throws Exception {
      Configuration config = ...;
      LoginContext loginCtx = new LoginContext("jackrabbit.oak", null, callbackHandler, config);
      loginCtx.login();  // works fine — bug only appears on second login after logout
      Subject subject = loginCtx.getSubject();
      assertNotNull(subject);  // bug not triggered
  }
  ```