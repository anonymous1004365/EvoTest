---
name: rolling-file-header-footer-lost-on-rollover
description: When header/footer content is written before file rollover detection,
  the header may be lost or corrupted in rolled files. Use this skill to detect header/footer
  write ordering bugs in trigger-based rolling file appenders.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# rolling-file-header-footer-lost-on-rollover

## Instructions

# Rolling File Header/Footer Lost on Rollover

## Instructions

- WHEN the TG encounters a rolling file appender that writes a **header** (via `writeHeader()` or similar) after file creation/adoption, and uses a **triggering policy** (e.g., `SizeBasedTriggeringPolicy`, `TimeBasedTriggeringPolicy`) that checks conditions during `append()` or `writeBytes()`:
  - THEN the TG should verify that the header is NOT written to the rolled (rotated) file, only to the active (current) file.
  - Specifically, test that after a rollover is triggered, the rolled file's content starts with the **actual log output** (e.g., log event data), NOT with the header content.

- WHEN the scenario involves a **triggering policy** that uses a **buffer size** or **byte count** to decide when to roll (e.g., implicit buffer writes, file length checks after writing):
  - THEN the TG should verify the ordering of operations: the header must be written **before** the triggering check occurs in the same append path, not after. The test should demonstrate that the header content appears correctly in the active file and does NOT get counted toward the triggering buffer/byte threshold.

- WHEN the appender has an **adopt** or **initialize** method that writes the header (e.g., `createManager` calling `writeHeader()`), AND this initialization path runs before the first `append()` call:
  - THEN the TG must ensure that the header bytes are written to the underlying stream/NIO channel directly, not through the same write path that checks rollover conditions. Test that if the header is the only content written, no rollover occurs prematurely.

- WHEN testing rolling file appenders with headers:
  - The TG should create a test that:
    1. Configures a rolling file appender with a **header** (e.g., an `HTMLLayout` which produces header/footer) and `append="false"`.
    2. Sets a small trigger size (e.g., `SizeBasedTriggeringPolicy size="1024"`).
    3. Writes enough log events to trigger at least one rollover.
    4. **Reads the rolled file** and asserts that the content starts with the expected log data (e.g., HTML body content), NOT with the HTML header content.
    5. **Reads the active file** and asserts that it contains the header content.
  - **Common pitfalls to avoid**:
    - Testing only the active file (current log file) — you must also check the rolled file content.
    - Assuming the header is written correctly just because no exceptions were thrown.
    - Testing only with text appenders — header/footer issues are especially common with layouts like `HTMLLayout` that produce distinct header/footer strings.
    - Not verifying that the footer is also correctly written/omitted in rolled files during shutdown/rollover.
    - Using `append="true"` without first asserting the header scenario with `append="false"` — the bug may manifest only when `append="false"` because the header is written during file creation.

### Correct test approach example:
```java
public void testHeaderFooterOnRollover() throws Exception {
    // Given: a RollingRandomAccessFile appender with HTMLLayout, append=false, small size trigger (1024 bytes)
    // Write enough log events to trigger rollover
    for (int i = 0; i < 100; i++) {
        logger.info("Log message " + i);
    }
    
    // When: the appender is closed/shutdown
    context.stop();
    
    // Then: the rolled file should NOT contain the HTML header
    String rolledContent = readFile("target/rolled1.log");
    // The header would be "<!DOCTYPE HTML..." — the rolled file should start with log body content
    assertFalse("Rolled file should not contain header", 
        rolledContent.startsWith("<!DOCTYPE HTML"));
    // The active file SHOULD contain the header
    String activeContent = readFile("target/test.log");
    assertTrue("Active file should contain header", 
        activeContent.startsWith("<!DOCTYPE HTML"));
}
```

### Incorrect test approach (missing the bug):
```java
// Only checks that no exception is thrown — misses the corrupted header in rolled file
public void testBasic() throws Exception {
    logger.info("test");
    context.stop();
    // No assertion on file content — useless for detecting this bug
}
```