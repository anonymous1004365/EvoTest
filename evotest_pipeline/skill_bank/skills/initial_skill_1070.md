---
name: appender-inheritance-on-configuration-reload
description: When a configuration is created from a different base (e.g., using XInclude),
  appenders from the preceding configuration may leak into the new configuration's
  root logger. Test that getAppenders() returns only the explicitly declared appenders
  after configuration.
code_tags:
- APPENDER_INHERITANCE
- CONFIGURATION_LOADING
test_pattern: STATE_TEST
---

# appender-inheritance-on-configuration-reload

## Instructions

# Appender Inheritance on Configuration Reload

## Instructions

WHEN the TG encounters a configuration creation mechanism that loads or assembles a `Configuration` from disparate sources (e.g., `XInclude`, composite config, property-based config) and the resulting `Configuration.getAppenders()` returns appenders that appear in the root logger but were NOT explicitly declared in the new configuration,

THEN the TG should write a test that:

1. Prepares a configuration file that declares appenders **only** in included sub-files (e.g., `xi:include`), not directly in the main configuration file's `<Appenders>` section.
2. Obtains the `LoggerContext` via a test rule (e.g., `LoggerContextRule`) that loads this configuration.
3. Calls `loggerContextRule.getConfiguration().getAppenders()` and asserts on the returned `Map<String, Appender>`.
4. Asserts that **only** the appenders explicitly present in the included sub-configuration files are present — no extra or inherited appenders from any other context or previous configuration state.
5. Specifically verifies the count (e.g., `assertEquals(2, appenders.size())`) and the presence of each appender by name (e.g., `assertThat(appenders, hasKey("STDOUT"))`).

**Common pitfalls to avoid:**
- Do NOT assume that `getAppenders()` returns only the appenders declared in the current configuration's `<Appenders>` block — it may include root logger appenders leaked from a previous configuration state.
- Do NOT test only for a specific appender being present without also verifying the total count — the bug is that **extra** (inherited) appenders are present.
- Do NOT rely on the `testConfiguredAppenders` method in a test subclass of an existing test — the same test may already exist in both the parent and child test classes, potentially masking the bug due to test framework inheritance.
- Make sure to obtain the configuration **after** it has been fully initialized/reconfigured, not during the construction phase.

**Example of a correct test:**

```java
@Test
public void testConfiguredAppenders() throws Exception {
    final LoggerContextRule loggerContextRule = new LoggerContextRule("log4j-xinclude.xml");
    final Configuration config = loggerContextRule.getConfiguration();
    final Map<String, Appender> appenders = config.getAppenders();
    // Should contain exactly the appenders from the included file, not extra inherited ones
    assertThat(appenders, hasSize(2));
    assertThat(appenders, hasKey("STDOUT"));
    assertThat(appenders, hasKey("FILE"));
}
```

**Example tests that pass on buggy version (incorrect):**

```java
// BAD — only checks for presence, not for absence of extra inherited appenders
@Test
public void testAppendersPresent() {
    final Map<String, Appender> appenders = config.getAppenders();
    assertNotNull(appenders.get("STDOUT")); // passes even if there's an extra inherited appender
}
```

```java
// BAD — uses getAppender() which only checks one appender
@Test
public void testRootAppender() {
    final Appender appender = config.getAppender("STDOUT");
    assertNotNull(appender); // passes even if the configuration has inherited extra appenders
}
```