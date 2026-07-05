---
name: session-id-strip-preserve-params
description: Tests for stripJSessionId should verify that arbitrary semicolon-delimited
  path parameters (not just jsessionid) are preserved when the session ID appears
  after them. When the session ID is not the first parameter, use the last index of
  `SESSION_ID_PARAM` instead of the first, to avoid stripping all preceding parameters.
code_tags:
- VALIDATION
- URL_SESSIONID_STRIPPING
test_pattern: PARAMETRIC_TEST
---

# session-id-strip-preserve-params

## Instructions

# Session ID Stripping Must Preserve Preceding Path Parameters

## Instructions

- WHEN the TG encounters `Strings.stripJSessionId(String)` method that uses `String.indexOf(SESSION_ID_PARAM)` (the first occurrence) 
- THEN it should test URLs where the session ID parameter (`;jsessionid=`) appears **after** other semicolon-delimited path parameters like `;a=b;c=d`
- The bug: the method used `indexOf(SESSION_ID_PARAM)` which finds the **first** `;jsessionid=`, but when `;jsessionid=` is not the first semicolon parameter, the code incorrectly strips everything from the **first** `;` through the session ID value. The fix is to use `lastIndexOf(SESSION_ID_PARAM)` instead.
- Test input example: `"http://localhost/abc;a=b;c=d;jsessionid=12345"` should yield `"http://localhost/abc;a=b;c=d"` (preserving `;a=b;c=d`)
- Test also the combination with query string: `"http://localhost/abc;a=b;c=d;jsessionid=12345?param=a;b"` should yield `"http://localhost/abc;a=b;c=d?param=a;b"`
- Verify that the returned string preserves all path parameters that appear **before** the session ID parameter
- Common pitfall: testing only URLs where `;jsessionid=` is the first/only semicolon parameter (e.g., `url + ";jsessionid=12345"`), which passes both before and after the fix — and missing the case with preceding parameters

### Correct Test Approach

```java
// Correct: tests with preceding path parameters
String url = "http://localhost/abc";

// WICKET-4816: path params before jsessionid must be preserved
assertEquals(url + ";a=b;c=d", 
    Strings.stripJSessionId(url + ";a=b;c=d;jsessionid=12345"));
assertEquals(url + ";a=b;c=d?param=a;b", 
    Strings.stripJSessionId(url + ";a=b;c=d;jsessionid=12345?param=a;b"));
```

### Common Mistake

```java
// Wrong: only testing jsessionid as the first param — won't catch the bug
String url = "http://localhost/abc";
assertEquals(url, Strings.stripJSessionId(url + ";jsessionid=12345"));
// This passes on both buggy and fixed versions
```