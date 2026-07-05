---
name: nested-file-statistics-accumulation
description: Use when testing file input formats that accumulate statistics (like
  file sizes) across multiple nested files. Teaches how to validate that cumulative
  statistics (total file sizes) are correctly computed when files are nested in subdirectories,
  not overcounted or undercounted.
code_tags:
- FILE_STATISTICS_ACCUMULATION
test_pattern: STATE_TEST
---

# nested-file-statistics-accumulation

## Instructions

# Nested File Statistics Accumulation

## Instructions

- WHEN the code under test is a `FileInputFormat` (or similar file-reading input format) that implements a `getStatistics(BaseStatistics cachedStats)` method returning a `FileBaseStatistics` object containing aggregated file statistics (e.g., total file size)
- THEN the TG should create a test that:
  1. Sets up a temporary directory containing **multiple nested subdirectories**, each with one or more files of known sizes
  2. Instantiates the input format (e.g., `EnumerateNestedFilesFormat`) and calls `format.getStatistics(null)` to compute statistics from scratch
  3. **Verifies that the reported total file size equals the sum of all file sizes across ALL nested subdirectories** — not just files in the top-level directory, and not double-counting any files
  4. Also verifies that **calling `getStatistics(stats)` with a previously returned statistics object** (simulating cached statistics) yields the same correct total

- **Common pitfalls**:
  - ❌ Testing only a single flat directory — this misses bugs where nested directory traversal is broken
  - ❌ Asserting the total size is non-zero or positive without checking the exact expected value — this misses overcounting/undercounting bugs
  - ❌ Forgetting that file sizes inside subdirectories must be **included** in the cumulative total (the bug may be that they are omitted)
  - ❌ Only testing `getStatistics(null)` without also testing `getStatistics(cachedStats)` — the bug may manifest differently with cached vs. fresh statistics

- **Correct example** (Java, JUnit 4):
  ```java
  @Test
  public void testGetStatisticsMultipleNestedFiles() throws IOException {
      File tempDir = temporaryFolder.newFolder();
      
      // Create nested structure: /tmp/sub1/file1.txt (100 bytes), /tmp/sub1/sub2/file2.txt (200 bytes)
      File sub1 = new File(tempDir, "sub1");
      sub1.mkdir();
      File file1 = new File(sub1, "file1.txt");
      writeFile(file1, 100);
      
      File sub2 = new File(sub1, "sub2");
      sub2.mkdir();
      File file2 = new File(sub2, "file2.txt");
      writeFile(file2, 200);
      
      EnumerateNestedFilesFormat format = new EnumerateNestedFilesFormat();
      format.setFilePath(new Path(tempDir.toURI().toString()));
      format.setNestedFileEnumeration(true);
      
      // Get statistics from scratch
      BaseStatistics stats = format.getStatistics(null);
      assertNotNull("Statistics should not be null", stats);
      assertEquals("Total file size should include all nested files",
          300L, stats.getTotalInputSize()); // Sum of ALL files across all subdirs = 100 + 200 = 300
      
      // Get statistics with cached stats
      BaseStatistics stats2 = format.getStatistics(stats);
      assertNotNull("Cached statistics should not be null", stats2);
      assertEquals("Cached statistics should match fresh statistics",
          300L, stats2.getTotalInputSize());
  }
  
  private void writeFile(File file, int size) throws IOException {
      try (FileOutputStream fos = new FileOutputStream(file)) {
          fos.write(new byte[size]);
      }
  }
  ```

- **Incorrect example** (would miss the bug):
  ```java
  @Test
  public void testGetStatisticsFlat() throws IOException {
      File tempDir = temporaryFolder.newFolder();
      File file1 = new File(tempDir, "file1.txt");
      writeFile(file1, 100);  // Only one file, no nesting
      
      EnumerateNestedFilesFormat format = new EnumerateNestedFilesFormat();
      format.setFilePath(new Path(tempDir.toURI().toString()));
      
      BaseStatistics stats = format.getStatistics(null);
      assertTrue("File size should be positive", stats.getTotalInputSize() > 0);
      // BUG: This assertion is too weak — it passes even if nested files are incorrectly counted
  }
  ```