---
name: token-credential-conflict-testing
description: When testing token-based authentication where a conflict occurs (e.g.,
  a token with the same key already exists), test that the provider gracefully handles
  the conflict by generating a different token instead of failing or returning null.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_CONSISTENCY
- CONFLICT_HANDLING
test_pattern: STATE_TEST
---

# token-credential-conflict-testing

## Instructions

# Token Credential Conflict Testing

## Instructions

- WHEN the TG encounters token provider logic that creates tokens with credentials involving a token key property that could conflict with an existing token (e.g., `TokenProviderImpl.createToken(TokenCredentials)` where the login token key is stored and then a new token with the same key is attempted)
- THEN the TG should write a test that:
  1. Obtains valid login credentials from a successful token creation (e.g., `tokenProvider.createToken(credentials)` returns a `TokenInfo`)
  2. Extracts the token key/user ID from the login credentials (e.g., `((TokenCredentials) info.getCredentials()).getUserId()` or the token property value)
  3. Creates new `TokenCredentials` with the **same** token key that was just created (simulating a duplicate key conflict)
  4. Calls `tokenProvider.createToken(conflictingCredentials)` and verifies that it still returns a non-null `TokenInfo`, not null
  5. Verifies the returned token is different (e.g., different token key) from the original
- The test should verify that the token provider handles the conflict gracefully by still creating a token (possibly with a modified key) rather than returning null or throwing an exception
- Common pitfalls:
  - Testing only the normal (non-conflict) case and assuming conflict handling works
  - Assuming the provider will throw an exception on conflict — check that it actually returns a valid TokenInfo
  - Forgetting to use the same token key string that would cause a conflict in the underlying storage
  - Not verifying the new token is actually different from the original

### Correct Example

```java
// Setup: Get initial credentials and create a token
TokenCredentials creds = new TokenCredentials("user1");
TokenInfo info = tokenProvider.createToken(creds);
assertNotNull(info);

// Get the token key from the login credentials (simulate conflict by reusing key)
String tokenKey = creds.getToken(); // or info.getToken()

// Create conflicting credentials with the same token key
TokenCredentials conflictingCreds = new TokenCredentials("user1");
conflictingCreds.setToken(tokenKey); // force the same key

// Attempt to create again with conflicting key
TokenInfo info2 = tokenProvider.createToken(conflictingCreds);

// Verify it doesn't return null despite the conflict
assertNotNull(info2);

// Verify the new token is different from the original
assertNotEquals(tokenKey, info2.getToken());
```

### Incorrect Example

```java
// WRONG: Only tests the normal path, assumes conflict is impossible
TokenCredentials creds = new TokenCredentials("user1");
TokenInfo info = tokenProvider.createToken(creds);
assertNotNull(info);

// Missing: no test for what happens when token key conflicts with existing token
```