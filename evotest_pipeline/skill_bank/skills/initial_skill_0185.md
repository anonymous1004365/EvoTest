---
name: impersonation-base-credenials-null-validation
description: WHEN tests involve ImpersonationCredentials wrapping a Subject, THEN
  the test should verify the code handles null/empty base credentials gracefully without
  NullPointerException. This skill teaches validating that getCredentials() or similar
  credential-retrieval logic properly extracts and validates credentials from impersonation
  wrappers.
code_tags:
- CONCURRENCY
- STATE_MUTATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# impersonation-base-credenials-null-validation

## Instructions

# Impersonation Base Credentials Null Validation

## Instructions

WHEN the TG encounters code that wraps or unwraps `ImpersonationCredentials` (i.e., `javax.jcr.security.ImpersonationCredentials`) to extract the base credentials, THEN it should write a test that:

1. Creates a `Subject` with a `Set<Credentials>` containing a `null` credential entry (since callbacks may result in null credential arrays)
2. Passes that Subject to the `login()` method or credential-extraction logic
3. Verifies that no `NullPointerException` or `NullPointerException`-related error occurs due to iterating over null values in the credential set
4. The test should expect `LoginException`, `FailedLoginException`, or `javax.security.auth.login.FailLoginException` (depending on the login module), NOT a `NullPointerException`

Concrete values from the actual bug:
- Use `new ImpersonationCredentials(otherCredentials, null)` — where `otherCredentials` is a `SimpleCredentials` and the second arg is `null` (the impersonation info)
- Use `ImpersonationCredentials` in the credentials set of a `Subject.getSubject(AccessController.getContext())`
- The affected method is in `LoginModuleImpl` or `AbstractLoginModule` where `getCredentials()` iterates over `subject.getSubject().getPublicCredentials(Credentials.class)` and may encounter null entries

Common pitfalls:
- Testing only valid impersonation scenarios — the TG must also test the invalid/edge case where impersonation credentials wrap null or missing base credentials
- Forgetting that when callbacks populate a credential array, some entries may be null; the login module must filter or skip null entries rather than blindly iterating
- Assuming credentials are always properly populated; tests should use `Set<Credentials>` containing `null` to simulate callback failures

Correct test approach:
```java
@Test(expected = javax.security.auth.login.LoginException.class)
public void testNullCredentialInImpersonation() throws Exception {
    // Setup with impersonation credentials wrapping another credential
    SimpleCredentials sc = new SimpleCredentials("test", "test".toCharArray());
    ImpersonationCredentials ip = new ImpersonationCredentials(sc, null);
    
    // Create a subject with null in the credential set
    final Subject subject = new Subject();
    subject.getPublicCredentials().add(null);
    
    // Login should fail with LoginException, NOT NullPointerException
    loginModule.login(subject);
}
```

Incorrect test approach (what the limited-view TG might do):
```java
// BAD: Only tests valid impersonation
@Test
public void testValidImpersonation() throws Exception {
    SimpleCredentials sc = new SimpleCredentials("admin", "admin".toCharArray());
    ImpersonationCredentials ip = new ImpersonationCredentials(sc, null);
    login(ip);
    assertTrue(loginModule.login());
}
```