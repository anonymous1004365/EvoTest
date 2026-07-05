---
name: xml-encoding-roundtrip-validation
description: This skill helps test XML parsers that accept String input containing
  multi-byte characters (like umlauts). It detects bugs where the parser silently
  produces mojibake (wrong encoding) rather than preserving characters correctly.
  Use this when testing parse(CharSequence) methods.
code_tags:
- ENCODING_AWARE_PARSING
- EXCEPTION_HANDLING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# xml-encoding-roundtrip-validation

## Instructions

# XML Encoding Roundtrip Validation

## Instructions

- WHEN the TG encounters an XML parser class (e.g. XmlPullParser) that has a `parse(CharSequence string)` method taking a CharSequence/String as input
- THEN the TG should write a test that creates a CharSequence containing multi-byte Unicode characters (e.g. German umlauts äöü, or any non-ASCII characters like éñç) and passes it to the parser's `parse` method. The test must retrieve the parsed text back (e.g. via `getText()` or `toString()`) and assert that the output characters match the input characters exactly — using `assertEquals(expected, actual)` on the full string content.
- The test must use **direct string literals** in the source code for the multi-byte characters (e.g. `"umlaut-äöü"`) and construct XML markup by concatenation, such as: `new CharSequence[] { "<tag1>umlaut-", "äöü", "</tag1>" }` — because the bug only manifests when a `CharSequence` passed to `parse` contains multi-byte characters.
- The TG should expect the test to **fail on the buggy version** with an assertion error showing mojibake (e.g. `expected:<umlaut-[äöü]> but was:<umlaut-[Ã¤Ã¶Ã¼]>`), i.e. the parser returns incorrectly encoded bytes instead of preserving the original characters. On the fixed version, the test should pass with characters preserved correctly.
- Common pitfalls to avoid:
  - ❌ Testing only with ASCII characters (no multi-byte) — this will not trigger the encoding bug.
  - ❌ Testing `parse(InputStream)` or `parse(InputStream, String encoding)` instead of `parse(CharSequence)` — the bug is specific to the CharSequence path.
  - ❌ Checking only that parsing succeeds (no exception) — the test must check the actual text content after parsing.
  - ❌ Reading the XML/string from an external file — the bug may be encoding-dependent; use inline string literals in the test.

**Correct Example** (triggers the encoding bug):
```java
@Test
public void encodingOfString() throws Exception
{
    XmlPullParser parser = new XmlPullParser();
    CharSequence[] input = new CharSequence[] { "<tag1>umlaut-", "äöü", "</tag1>" };
    parser.parse(input);
    // On buggy version: toString() returns "umlaut-Ã¤Ã¶Ã¼" (mojibake)
    // On fixed version: toString() returns "umlaut-äöü" (correct)
    assertEquals("umlaut-äöü", parser.toString());
}
```

**Incorrect Example** (will not catch the bug):
```java
@Test
public void encodingOfString_incorrect() throws Exception
{
    XmlPullParser parser = new XmlPullParser();
    parser.parse("<tag1>hello</tag1>");  // ❌ No multi-byte characters
    assertEquals("<tag1>hello</tag1>", parser.toString());
}
```