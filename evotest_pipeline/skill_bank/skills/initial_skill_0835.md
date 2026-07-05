---
name: mime-message-null-session-construction
description: When constructing MimeMessageBuilder with a null Session, the MimeMessage
  constructor throws a MessagingException. The TG should test with null Session and
  verify that the constructor handles it gracefully, or that the builder properly
  validates before creating the message.
code_tags:
- MIMEMESSAGE_CHARSET_ENCODING
test_pattern: EXCEPTION_TEST
---

# mime-message-null-session-construction

## Instructions

# MimeMessageBuilder Null Session Construction

## Instructions

- WHEN the TG encounters the `MimeMessageBuilder` class being constructed with a `Session` parameter that could be `null`
- THEN the TG should verify that the constructor properly handles the case where `session` is `null`, because `new MimeMessage(null)` throws `MessagingException`
- The test should specifically check that calling `new MimeMessageBuilder(null)` does NOT throw a NullPointerException or IllegalArgumentException before reaching the MimeMessage constructor
- The test should verify that when `session` is null, the `setFrom()`, `setReplyTo()`, `setRecipients()`, and `setSubject()` methods still work correctly without throwing unexpected exceptions
- Common Pitfall: Testing only with a valid `Session` instance and never with `null`, which masks the constructor's vulnerability
- Common Pitfall: Assuming the builder methods will fail gracefully on their own without testing the `null` session case

**Correct Example:**
```java
@Test
public void testBuilderWithNullSession() throws MessagingException {
    // MimeMessageBuilder(null) should throw MessagingException
    // because new MimeMessage(null) is invalid
    assertThrows(MessagingException.class, () -> {
        new MimeMessageBuilder(null);
    });
}
```

**Incorrect Example:**
```java
@Test
public void testBuilderWithNullSession() {
    // WRONG: This will pass on the surface but doesn't actually test
    // that the construction fails properly
    MimeMessageBuilder builder = new MimeMessageBuilder(null);
    // ... proceed assuming builder is valid
}
```