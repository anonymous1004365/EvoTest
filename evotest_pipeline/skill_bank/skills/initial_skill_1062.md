---
name: script-decoration-null-handling
description: When implementing script decoration methods like preDecorateScript/postDecorateScript
  that chain to decorated listeners, test that null return values are properly handled
  and do not cause NullPointerException. The decorator must gracefully skip null scripts.
code_tags:
- AJAX_SCRIPT_DECORATION
- NULL_CHECK
- SCRIPT_NULL_HANDLING
test_pattern: EXCEPTION_TEST
---

# script-decoration-null-handling

## Instructions

# Script Decoration Null Handling

## Instructions

- WHEN the TG encounters an implementation of `IAjaxCallListener` that acts as a decorator (e.g., `AjaxPreprocessingCallDecorator`), and the decorator's `preDecorateScript(Component, String)` or `postDecorateScript(Component, String)` methods chain to a wrapped/decorated listener
- THEN the TG should test that when the wrapped listener's script method returns `null`, the decorator does NOT throw a `NullPointerException`. The test should:
  1. Create a mock/stub of `IAjaxCallListener` whose `postDecorateScript(Component, String)` returns `null`
  2. Create the decorator wrapping this mock
  3. Call `postDecorateScript(component, "someScript()")` on the decorator
  4. Assert that the call completes without throwing any exception and returns the input script unchanged (the original input script should be passed through when the wrapped listener returns null)

- WHEN the TG writes such a test, it must verify that the decorator correctly handles null returns from wrapped listeners by either:
  - Returning the original `script` parameter when the wrapped listener returns null
  - Returning the wrapped listener's result when it is non-null
  - Verify this with assertions on the return value

- Common pitfalls to avoid:
  - Testing only the non-null case (where the wrapped listener returns a modified script) while missing the null-case scenario
  - Assuming the empty string is equivalent to null — these are distinct cases and both should be tested
  - Forgetting to verify that the original script is returned when the wrapper returns null (the decorator should pass through the original script, not null)

### Correct Example:
```java
@Test
public void testPostDecorateScriptWithNullFromWrappedListener()
{
    // mock a listener that returns null from postDecorateScript
    IAjaxCallListener wrapped = new IAjaxCallListener()
    {
        @Override
        public CharSequence postDecorateScript(Component component, CharSequence script)
        {
            return null;
        }
        // ... other methods with default implementations
    };
    
    AjaxPreprocessingCallDecorator decorator = new AjaxPreprocessingCallDecorator(wrapped);
    CharSequence result = decorator.postDecorateScript(mockComponent, "originalScript();");
    
    // The decorator must not throw NPE and should pass through the original script
    Assert.assertEquals("originalScript();", result);
}
```

### Incorrect Example (misses the null case):
```java
@Test
public void testPostDecorateScript()
{
    IAjaxCallListener wrapped = new IAjaxCallListener()
    {
        @Override
        public CharSequence postDecorateScript(Component component, CharSequence script)
        {
            return "modified_" + script;
        }
        // ...
    };
    
    AjaxPreprocessingCallDecorator decorator = new AjaxPreprocessingCallDecorator(wrapped);
    CharSequence result = decorator.postDecorateScript(mockComponent, "script();");
    
    Assert.assertEquals("modified_script();", result);
    // This test passes on the buggy version too, missing the NPE bug entirely
}
```