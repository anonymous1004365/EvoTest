---
name: os-activation-profile-reversal-testing
description: WHEN testing OS-based profile activation with reversed (negated) name
  matching using the '!' prefix, THEN the test must verify that a profile with os.name
  set to "!dddd" (where "dddd" does NOT match the current OS name) is correctly activated.
  This skill tests the negation logic in OperatingSystemProfileActivator's determineNameMatch
  method.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STRING_FORMATTING
test_pattern: PARAMETRIC_TEST
---

# os-activation-profile-reversal-testing

## Instructions

# OS Activation Profile Reversal Testing

## Instructions

### WHEN the TG encounters:
- A `ProfileActivator` implementation (either `org.apache.maven.model.profile.activation.OperatingSystemProfileActivator` or the deprecated `org.apache.maven.profiles.activation.OperatingSystemProfileActivator`) that determines profile activation based on OS properties, AND
- The activation logic supports negation using a `"!"` prefix on OS fields (name, family, arch, version), where `"!xxx"` means "activate if the current OS does NOT match xxx"

### THEN the TG should:

1. **Test reversed (negated) OS name matching by using a name that is guaranteed NOT to match the current OS:**
   - Create an `ActivationOS` object and set its name to `"!dddd"` (a name that does not match any real OS like Linux, Windows, Mac OS X, etc.)
   - Create a `Profile` with this activation OS
   - Call the activator's `isActive()` method
   - **Expect `true`** — because `Os.isName("dddd")` returns `false`, and the negation `!false` should evaluate to `true`
   - On the buggy version, this may incorrectly return `false`

2. **Test reversed (negated) OS name matching by using a name that DOES match the current OS:**
   - Create an `ActivationOS` object with name set to `"!${os.name}"` (or more practically, get the property `os.name` from `System.getProperties()` and prepend `"!"`)
   - Call the activator's `isActive()` method
   - **Expect `false`** — because `Os.isName(osName)` returns `true`, and the negation `!true` should evaluate to `false`

3. **Test the exact OS name match (without negation) also works correctly:**
   - Create an `ActivationOS` with name set to some non-matching name like `"dddd"` (no `"!"` prefix)
   - Expect `false` from `isActive()`
   - Create an `ActivationOS` with name set to the actual current OS name (from `System.getProperty("os.name")`)
   - Expect `true` from `isActive()`

4. **Use the actual activator classes directly (not the ProfileManager pipeline):**
   - For the newer activator: `new org.apache.maven.model.profile.activation.OperatingSystemProfileActivator().isActive(profile, context, problems)`
   - For the deprecated activator: `new org.apache.maven.profiles.activation.OperatingSystemProfileActivator().isActive(profile)`
   - This avoids complexity from the ProfileManager flow and tests just the OS activation logic

### Common pitfalls to avoid:
- ❌ **Testing only with the `family` field** — The bug may be specific to one field (e.g., `name` vs `family`). Test each OS field (`name`, `family`, `arch`, `version`) independently.
- ❌ **Using a name that coincidentally matches the OS** — Using "!linux" on a Linux machine means `Os.isName("linux")` returns `true`, so the negated result is `false` — which looks correct but doesn't test the negation logic. Always use a deliberately non-matching name like "!dddd".
- ❌ **Calling `ProfileManager.getActiveProfiles()` instead of the activator directly** — The ProfileManager may have additional filtering, caching, or conditional logic that masks the bug.
- ❌ **Not importing `ActivationOS`** — The model class is `org.apache.maven.model.ActivationOS` (note: no 'e' in 'OS'), not a different class.

### Example test pattern (correct):

```java
public void testOsNameNegationShouldActivate()
{
    Profile profile = new Profile();
    Activation activation = new Activation();
    ActivationOS os = new ActivationOS();
    os.setName( "!dddd" );  // "dddd" does NOT match any real OS
    activation.setOs( os );
    profile.setActivation( activation );
    
    OperatingSystemProfileActivator activator = new OperatingSystemProfileActivator();
    boolean active = activator.isActive( profile );
    
    assertTrue( "Profile with os.name '!dddd' should be active since 'dddd' does not match current OS", active );
}
```

### Common mistake (incorrect):

```java
// INCORRECT: Uses ProfileManager pipeline instead of direct activator
ProfileManager profileManager = new DefaultProfileManager( getContainer(), props );
profileManager.addProfile( osActivated );
List active = profileManager.getActiveProfiles( null );
assertEquals( 1, active.size() );  // This may pass/fail for wrong reasons
```

```java
// INCORRECT: Uses a name that might match the current OS
os.setName( "!linux" );  // On Linux, this returns false (correctly negated), but doesn't prove negation works
// Instead use "!dddd" which is guaranteed non-matching
```