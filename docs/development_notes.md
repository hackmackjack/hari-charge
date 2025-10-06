# Development Notes

## Data Model Refactor (2025-10-05)

This update refactors the faculty-course relationship to create a single source of truth, resolving the root cause of the faculty-student visibility issue.

### 1. Automated Faculty-Course Linkage
-   **Issue:** The "Courses Taught" (`course_ids`) field on the faculty model was a manual `Many2many` field. This required manual data entry, which was error-prone and led to an unreliable link between faculty and their courses, causing the "Students" tab to be empty.
-   **Fix (`op.faculty` model):** The `course_ids` field has been refactored into a **computed and stored** field.
    -   It now automatically calculates the courses a faculty teaches based on their assigned subjects (`faculty_subject_ids`).
    -   This change establishes `faculty_subject_ids` as the single source of truth.
-   **Impact:** This ensures the link between faculty and courses is always accurate and automatic, which in turn fixes the logic for the "Students" tab and the faculty security rules. The system is now more robust and less dependent on manual data entry.

---

## Data Integrity Fix (2025-10-05)

This update addresses a critical data linkage issue where the connection between a user and their faculty profile was not being automatically established, causing record rules and computed fields to fail.

### 1. Automated User-Faculty Linking
-   **Issue:** The `faculty_id` field on the `res.users` model was not being populated when a faculty record was created or linked to a user. This resulted in faculty members being unable to see their students, as the system could not identify them correctly.
-   **Fix (`op.faculty` model):** The `create` and `write` methods of the `op.faculty` model have been overridden.
    -   On **create**, the new logic automatically finds the user associated with the faculty's partner record and writes the faculty's ID to the user's `faculty_id` field.
    -   On **write**, if the partner is changed, the logic first clears the `faculty_id` from the old user's record and then populates it for the new user, ensuring the link is always accurate.
-   **Impact:** This ensures a robust, automated data link between `res.users` and `op.faculty`, guaranteeing that security rules and related data fields function correctly.

---

## Usability Enhancements (2025-10-05)

This update introduces new computed fields and view modifications to improve the user experience for faculty and administrators by making relational data more accessible.

### 1. Enhanced Faculty View with Student Information
-   **Model Change (`op.faculty`):** Added a new computed `Many2many` field, `student_ids`, to the faculty model. This field dynamically calculates and displays all students enrolled in the courses taught by that faculty member.
-   **View Change (`faculty_view.xml`):**
    -   The `course_ids` field is now displayed as a tag widget directly on the faculty form for better visibility.
    -   A new "Students" tab has been added to the faculty form, containing a list view of the new `student_ids` field.

### 2. Enhanced Course View with Faculty Information
-   **Model Change (`op.course`):** Added a new computed `Many2many` field, `faculty_ids`, to the course model. This field aggregates and shows all faculty members who teach subjects within that course.
-   **View Change (`course_view.xml`):**
    -   A new "Faculty" tab has been added to the course form, which displays a list of all faculty members associated with the course via the `faculty_ids` field.

---

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