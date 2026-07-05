---
name: multipart-form-tester-submit-without-upload
description: When using FormTester to submit a multipart form without any file upload,
  the TG should verify that the form submission correctly handles the null/empty file
  upload case without errors. This skill ensures multipart forms work when only setting
  text values without file attachments.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_TRANSITION
test_pattern: STATE_TEST
---

# multipart-form-tester-submit-without-upload

## Instructions

# Multipart Form Submission Without File Upload

## Instructions

- WHEN the TG encounters a test that uses `FormTester` to submit a form backed by a `FileUploadField` (multipart form)
- THEN it should test the scenario where the form is submitted with only text/regular form component values and NO file upload (no call to `formTester.setFile(...)`), on a form where the `FileUploadField` is not required
- The test should call `formTester.setValue("text", "Mock Value")` and then `formTester.submit()` without ever calling `setFile()`, and verify that:
  - `formTester.getForm().hasError()` returns `false` (the form has no validation errors)
  - The `FileUploadField`'s `getFileUpload()` returns `null` (no upload occurred)
  - The regular form component values are properly propagated (e.g., domain object's text field equals "Mock Value")
- **Common pitfall**: Only testing multipart forms with file uploads, or only testing that validation errors appear when a required FileUploadField is empty. The TG might miss the case where a multipart form with an **optional** FileUploadField is submitted without any file — the bug is that the `FormTester` might fail to properly handle null file upload state during form submission.

**Correct example:**
```java
tester.startPage(MockFormFileUploadPage.class, new PageParameters("required=false"));
MockFormFileUploadPage page = (MockFormFileUploadPage)tester.getLastRenderedPage();
MockDomainObjectFileUpload domainObject = page.getDomainObject();

FormTester formTester = tester.newFormTester("form");
formTester.setValue("text", "Mock Value");
formTester.submit();

assertFalse(formTester.getForm().hasError());
assertNull(page.getFileUpload());
assertEquals("Mock Value", domainObject.getText());
```

**Incorrect example (no test for optional upload):**
```java
// Only tests with file upload, missing the no-upload multipart case
FormTester formTester = tester.newFormTester("form");
formTester.setFile("file", new File("pom.xml"), "text/xml");
formTester.setValue("text", "Mock value");
formTester.submit();
// Missing test: what happens when submit() is called on a multipart form without setFile()?
```