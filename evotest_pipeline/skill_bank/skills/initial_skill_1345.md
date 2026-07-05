---
name: token-validation-case-insensitivity
description: When validating login tokens that encode a user ID, test that token validation
  is case-insensitive with respect to the user ID. Use this skill when a token-based
  authentication provider compares the userId from the token against the current user's
  ID.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# token-validation-case-insensitivity

## Instructions

# Token Validation is Case-Insensitive for User ID

## Instructions

- WHEN the TG encounters a token-based authentication provider that stores a user ID in a token and later compares it with the current user's ID (e.g., `TokenProviderImpl.getTokenInfo(String token)` which returns a `TokenInfo` whose `getUserId()` is compared with the current `userId`)
- THEN the TG should write a test that creates a token for a user using one case (e.g., `"admin"`), then authenticates with that token under a different case (e.g., `"ADMIN"`), and verifies that the token validation succeeds and the returned user ID matches the original (stored) case.
- The test should verify that calling `getTokenInfo(token)` does NOT throw an exception, and that the resulting `TokenInfo.getUserId()` returns the originally registered user ID.
- Common pitfalls to avoid:
  - Testing only with identical-cased user IDs (e.g., `"admin"` login with `"admin"` token) — this doesn't catch case-sensitivity bugs
  - Using a user ID that is entirely numeric — case differences can't be observed
  - Assuming the token validation method does an exact/equals comparison — it should do case-insensitive comparison (e.g., `equalsIgnoreCase`)
  - Not verifying that the returned `userId` matches the originally registered case (e.g., `"admin"` not `"ADMIN"`)

**Correct example (catches this bug):**
```java
@Test
public void testTokenValidationIsCaseInsensitive() throws Exception {
    // Register a token for "admin" (lowercase)
    TokenInfo tokenInfo = tokenProvider.createToken("admin", Collections.emptyMap());
    assertNotNull(tokenInfo);
    String token = tokenInfo.getToken();
    
    // Validate with "ADMIN" (uppercase) — this should succeed
    TokenInfo validatedInfo = tokenProvider.getTokenInfo(token);
    assertNotNull(validatedInfo);
    assertEquals("admin", validatedInfo.getUserId());  // Must return original case "admin"
    
    // Also verify: token login with "admin" still works
    assertTrue(tokenProvider.authenticate(token));
}
```

**Incorrect example (misses the bug):**
```java
@Test
public void testTokenValidation() throws Exception {
    TokenInfo tokenInfo = tokenProvider.createToken("admin", Collections.emptyMap());
    assertNotNull(tokenInfo);
    // Only tests with same case — doesn't catch case-sensitivity bug
    TokenInfo validatedInfo = tokenProvider.getTokenInfo(tokenInfo.getToken());
    assertNotNull(validatedInfo);
    assertEquals("admin", validatedInfo.getUserId());
}
```