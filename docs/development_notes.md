# Development Notes

## Final Solution: Faculty-Student Visibility (2025-10-06)

This document outlines the complete and final implementation for the faculty-student visibility feature, incorporating all necessary data model changes, security rules, and UI enhancements.

### 1. The Core Problem
Faculty users were unable to see their assigned students, both in the "Students" tab on their profile and in the main "Students" list view. This was due to several underlying issues in the data model and security rules.

### 2. The Final, Correct Implementation

#### a. Data Model and Linkage
-   **User-Faculty Link (`res.users.faculty_id`):** A `faculty_id` field was added to the `res.users` model (`tarcin_core/models/res_users.py`) to create a direct link to a faculty profile.
-   **Automated Link Maintenance (`op.faculty`):** The `create` and `write` methods on the `op.faculty` model were overridden to automatically populate this `faculty_id` on the user record, ensuring the link is always maintained.
-   **Automated Course Linkage (`op.faculty.course_ids`):** The `course_ids` field on the `op.faculty` model was refactored into a **computed, stored field**. It now automatically determines the courses a faculty teaches based on their assigned subjects (`faculty_subject_ids`), establishing a single source of truth.
-   **Corrected Student Linkage (`op.faculty.student_ids`):** The `_compute_student_ids` method was corrected to search through the `op.student.course` enrollment model, which accurately gathers all students enrolled in the faculty's courses.

#### b. Security and Access Control
-   **Corrected Record Rule:** The student visibility record rule (`rule_student_faculty_course`) in `tarcin_core/security/op_security.xml` was updated with a more precise, subject-based domain: `[('course_detail_ids.subject_ids', 'in', user.faculty_id.faculty_subject_ids.ids)]`. This correctly filters students based on the subjects they share with the faculty.
-   **Admin Permissions:** The `group_op_back_office` was corrected to no longer inherit from `group_op_faculty`, ensuring administrators have full, unrestricted access.

#### c. UI Enhancements
-   **Faculty View (`faculty_view.xml`):** A "Students" tab was added to display the `student_ids` list, and the computed `course_ids` field was made visible and read-only.
-   **Course View (`course_view.xml`):** A "Faculty" tab was added to display the computed `faculty_ids` list, showing all teachers for a course.

### 3. Final Impact
This comprehensive solution resolves all reported issues. The data model is now robust, automated, and less prone to error. Faculty users can correctly see their students in all relevant views, and the security rules function as intended.