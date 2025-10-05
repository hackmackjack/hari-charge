# Development Notes

## Security and Access Control Fix (2025-10-05)

This update resolves a critical application crash and corrects permission structures based on engineering feedback. The new implementation is more robust and follows Odoo best practices.

### 1. Resolved Application Crash by Extending `res.users`

-   **Issue:** The application was failing to load due to an `AttributeError`. A record rule (`rule_student_faculty_course`) was trying to access `user.faculty_id`, but this field did not exist on the `res.users` model.
-   **Fix:** Instead of creating a complex domain, the `res.users` model was extended directly.
    -   A new file, `tarcin_core/models/res_users.py`, was created to add a `faculty_id` `Many2one` field to `res.users`, creating a direct link to the corresponding faculty record.
    -   The new model file was imported into `tarcin_core/models/__init__.py` to ensure it is loaded by Odoo.
-   **Impact:** With the `user.faculty_id` field now available, the original record rule domain `[('course_id', 'in', user.faculty_id.course_ids.ids)]` is valid and functions as intended, resolving the crash.

### 2. Corrected Administrator Group Inheritance

-   **Issue:** The administrator account was being incorrectly restricted by faculty-level security rules due to improper group inheritance.
-   **Fix:** In `tarcin_core/security/op_security.xml`, the `group_op_faculty` was removed from the `implied_ids` list of the `group_op_back_office` group.
-   **Impact:** This change ensures that administrators have full, unrestricted access and are not affected by security rules designed for the faculty role.