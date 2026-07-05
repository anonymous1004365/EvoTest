---
name: password-history-exception-propagation
description: When testing password history validation that throws PasswordHistoryException,
  verify that the exception message is propagated to the credentials attribute. This
  skill applies when the authentication flow catches PasswordHistoryException and
  should store its message in SimpleCredentials under the key PasswordHistoryException.class.getSimpleName().
code_tags:
- EXCEPTION_HANDLING
- NULL_CHECK
test_pattern: STATE_TEST
---

# password-history-exception-propagation

## Instructions

# Password History Exception Propagation Testing

## Instructions

- WHEN testing a password change flow that triggers password history validation (i.e., the `changePassword` method in `UserAuthentication` catches a `PasswordHistoryException` thrown by `PasswordHistory.checkPasswordInHistory()` or `PasswordHistory.updatePasswordHistory()`)
- THEN the TG should verify that the caught exception's message (`e.getMessage()`) is stored as an attribute on the `SimpleCredentials` object under the key `PasswordHistoryException.class.getSimpleName()` (i.e., `"PasswordHistoryException"`)
- The TG should also verify that `CredentialExpiredException` is re-thrown (so the outer `authenticate` call still throws `CredentialExpiredException`)
- WHEN testing scenarios where password history DOES NOT apply (e.g., password validation fails before history checking), THEN the TG must verify that `PasswordHistoryException` attribute is NOT set on the credentials (remains `null`)
- Include test cases where:
  1. The new password is identical to the current password → expects message `"New password is identical to the current password."`
  2. The new password matches an entry in the history (i.e., a previously used password that is different from the current one) → expects message `"New password was found in password history."`
  3. The new password fails validation (e.g., too short / doesn't meet constraints) before history is even checked → expects `PasswordHistoryException` attribute to be `null`
- Common pitfalls:  
  - Testing only that `CredentialExpiredException` is thrown and forgetting to check the credentials attribute for the failure reason  
  - Not testing the case where the new password is the same as current (different exception message than history match)  
  - Testing with unprotected credentials (missing `UserConstants.CREDENTIALS_ATTRIBUTE_NEWPASSWORD` attribute) — that path won't trigger password change at all  
- Correct example:  
  ```java
  @Test  
  public void testPasswordHistoryRejectsReusedPassword() {  
      // Setup: user changes password to pw1, expire it, then try pw1 again  
      User user = getTestUser();  
      user.changePassword("pw12345678");  
      Authentication a = new UserAuthentication(getUserConfiguration(), root, userId);  
      root.getTree(user.getPath()).getChild(UserConstants.REP_PWD)  
              .setProperty(UserConstants.REP_PASSWORD_LAST_MODIFIED, 0);  
      root.commit();  
      // First authenticate to trigger expiry  
      a.authenticate(new SimpleCredentials(userId, "pw12345678".toCharArray()));  
      // This should throw CredentialExpiredException  
      SimpleCredentials creds = new SimpleCredentials(userId, "pw12345678".toCharArray());  
      creds.setAttribute(UserConstants.CREDENTIALS_ATTRIBUTE_NEWPASSWORD, userId);  
      CredentialExpiredException thrown = assertThrows(CredentialExpiredException.class, () -> a.authenticate(creds));  
      assertEquals("New password was found in password history.",  
              creds.getAttribute(PasswordHistoryException.class.getSimpleName()));  
  }  
  ```  
- Incorrect example:  
  ```java  
  @Test  
  public void testPasswordHistoryRejectsReusedPassword_BAD() {  
      // BAD: only checks exception type, doesn't verify attribute  
      User user = getTestUser();  
      user.changePassword("pw12345678");  
      Authentication a = new UserAuthentication(getUserConfiguration(), root, userId);  
      root.getTree(user.getPath()).getChild(UserConstants.REP_PWD)  
              .setProperty(UserConstants.REP_PASSWORD_LAST_MODIFIED, 0);  
      root.commit();  
      SimpleCredentials creds = new SimpleCredentials(userId, "pw12345678".toCharArray());  
      creds.setAttribute(UserConstants.CREDENTIALS_ATTRIBUTE_NEWPASSWORD, userId);  
      assertThrows(CredentialExpiredException.class, () -> a.authenticate(creds));  
      // Missing: verify that failure reason message is propagated  
  }  
  ```