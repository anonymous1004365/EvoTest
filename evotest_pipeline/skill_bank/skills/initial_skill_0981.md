---
name: form-tester-fileupload-submit-without-file
description: WHEN testing FormTester with forms that contain FileUploadField components,
  THEN test that calling form.submit() without setting a file on the FileUploadField
  does not cause a NullPointerException. This skill helps detect missing null-checks
  on FileUploadField file values during form submission.
code_tags:
- VALIDATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# form-tester-fileupload-submit-without-file

## Instructions

# FormTester FileUpload Submission Without File

## Instructions

- WHEN the Test Generator (TG) encounters a test using `FormTester` that processes a form containing a `FileUploadField` component (from `org.apache.wicket.markup.html.form.upload.FileUploadField`)
- THEN the TG SHOULD:
  1. Create a test that calls `tester.newFormTester("formId")` on a form that includes a `FileUploadField`
  2. Call `formTester.submit()` WITHOUT first setting any file value on the `FileUploadField`
  3. Assert that `formTester.submit()` completes without throwing any exception — specifically, that no `NullPointerException` is thrown due to a null `FileUpload` value from the `FileUploadField`

- The TG MUST verify that the `FormTester.submit()` method handles the case where a `FileUploadField` exists in the form but the user has not uploaded any file (i.e., `FileUploadField.getFileUpload()` returns `null`). The fix should have added a null check before dereferencing the `FileUpload` object.

- Common pitfalls to avoid:
  - Assuming that forms with `FileUploadField` always need a file to be set before submission — this misses the null case
  - Only testing with a file provided via `MockFormFileUploadPage` or similar setup that pre-populates uploads — this misses the empty/no-file case
  - Not including a `FileUploadField` in the form under test at all — the bug only manifests when `FileUploadField` is present but has no file value

### Example (correct test structure):

```java
@Test
public void testSubmitWithoutUploadFile()
{
    // Start a page that contains a form with a FileUploadField
    tester.startPage(MockFormFileUploadPage.class);

    // Create a FormTester for the form
    FormTester formTester = tester.newFormTester("form");

    // Submit WITHOUT setting any file
    // No NullPointerException should be thrown
    formTester.submit();
}
```

### Example (incorrect — what to avoid):

```java
@Test
public void testSubmitWithUploadFile()
{
    tester.startPage(MockFormFileUploadPage.class);
    FormTester formTester = tester.newFormTester("form");
    
    // ❌ Only tests with a file — won't detect the null case bug
    formTester.setFile("fileUploadField", new File("test.txt"), "text/plain");
    formTester.submit(); // passes even with the bug
}
```