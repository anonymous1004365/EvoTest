---
name: url-src-attribute-html-escaping
description: When writing URLs into HTML src attributes, test that the URL is NOT
  HTML-escaped (it should go directly into the attribute), while other attributes
  like id and charset ARE HTML-escaped. Use a StringResponse capturing utility and
  assert on the full rendered string.
code_tags:
- DATE_PARSE_FORMAT
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# url-src-attribute-html-escaping

## Instructions

# URL src Attribute HTML Escaping

## Instructions

- WHEN the TG encounters a method that writes a `src` attribute with a URL alongside other HTML attributes (`id`, `charset`, `defer`, `async`) to a response, such as `JavaScriptUtils.writeJavaScriptUrl(Response, CharSequence, String, boolean, String, boolean)`
- THEN the TG should verify that the URL written in `src="..."` is rendered as-is WITHOUT HTML escaping (e.g., `&` stays as `&`, not `&amp;`), while attribute values like `id` and `charset` ARE HTML-escaped using `Strings.escapeMarkup()`. Use a `StringResponse` to capture output and assertEquals on the full expected string.
- Common pitfalls to avoid:
  - NOT testing that `&` in the URL is preserved as `&` rather than escaped to `&amp;`
  - Testing only with simple URLs that lack session IDs or query parameters (`?`, `&`, `;`)
  - Assuming the `src` attribute value goes through the same escaping as `id`/`charset`
  - Forgetting that the `src` URL is written directly via `response.write(url)` with no escaping wrapper

**Correct example (testing writeJavaScriptUrl with all params):**
```java
StringResponse response = new StringResponse();
String url = "some/url;jsessionid=1234?p1=v1&p2=v2";
String id = "some&bad%id";
boolean defer = true;
boolean async = true;
String charset = "some&bad%%charset";
JavaScriptUtils.writeJavaScriptUrl(response, url, id, defer, charset, async);

assertEquals(
    "<script type=\"text/javascript\" id=\"some&amp;bad%id\" defer=\"defer\" async=\"async\" charset=\"some&amp;bad%%charset\" src=\"some/url;jsessionid=1234?p1=v1&p2=v2\"></script>\n",
    response.toString());
```

**Incorrect example (testing without preserving `&` in URL):**
```java
StringResponse response = new StringResponse();
JavaScriptUtils.writeJavaScriptUrl(response, "test.js", null);
// This does NOT verify that & in query parameters is preserved
// A URL like "test.js?q=1&r=2" would silently produce wrong output if & became &amp;
assertEquals(
    "<script type=\"text/javascript\" src=\"test.js\"></script>\n",
    response.toString());
// BUG: Only tests a simple URL, misses the URL escaping issue entirely
```