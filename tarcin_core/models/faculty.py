# -- coding: utf-8 --
###############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpFaculty(models.Model):
    _name = "op.faculty"
    _description = "OpenEduCat Faculty"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {"res.partner": "partner_id"}
    _parent_name = False
    
    partner_id = fields.Many2one('res.partner', 'Partner',
                                 required=True, ondelete="cascade")
    first_name = fields.Char('First Name', translate=True, required=True)
    middle_name = fields.Char('Middle Name', size=128)
    last_name = fields.Char('Last Name', size=128, required=True)
    birth_date = fields.Date('Birth Date', required=True)
    blood_group = fields.Selection([
        ('A+', 'A+ve'),
        ('B+', 'B+ve'),
        ('O+', 'O+ve'),
        ('AB+', 'AB+ve'),
        ('A-', 'A-ve'),
        ('B-', 'B-ve'),
        ('O-', 'O-ve'),
        ('AB-', 'AB-ve')
    ], string='Blood Group')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], 'Gender', required=True)
    nationality = fields.Many2one('res.country', 'Nationality')
    emergency_contact = fields.Many2one(
        'res.partner', 'Emergency Contact')
    id_number = fields.Char('ID Card Number', size=64)
    login = fields.Char(
        'Login', related='partner_id.user_id.login', readonly=True)
    last_login = fields.Datetime('Latest Connection', readonly=True,
                                 related='partner_id.user_id.login_date')
    course_ids = fields.Many2many(
        'op.course', string='Courses Taught',
        compute='_compute_course_ids', store=True)
    faculty_subject_ids = fields.Many2many('op.subject', string='Subject(s)',
                                           tracking=True)
    emp_id = fields.Many2one('hr.employee', 'HR Employee')
    main_department_id = fields.Many2one(
        'op.department', 'Main Department',
        default=lambda self:
        self.env.user.dept_id and self.env.user.dept_id.id or False)
    allowed_department_ids = fields.Many2many(
        'op.department', string='Allowed Department',
        default=lambda self:
        self.env.user.department_ids and self.env.user.department_ids.ids or False)
    active = fields.Boolean(default=True)
    student_ids = fields.Many2many(
        'op.student',
        string='Students',
        compute='_compute_student_ids',
        readonly=True,
        help="Students who are enrolled in the courses taught by this faculty."
    )

    @api.depends('faculty_subject_ids')
    def _compute_course_ids(self):
        """Computes the courses that include subjects taught by this faculty."""
        for faculty in self:
            if faculty.faculty_subject_ids:
                courses = self.env['op.course'].search([
                    ('subject_ids', 'in', faculty.faculty_subject_ids.ids)
                ])
                faculty.course_ids = courses
            else:
                faculty.course_ids = False

    @api.depends('course_ids')
    def _compute_student_ids(self):
        """Computes the students who are in the courses taught by this faculty."""
        for faculty in self:
            if faculty.course_ids:
                student_courses = self.env['op.student.course'].search([
                    ('course_id', 'in', faculty.course_ids.ids)
                ])
                faculty.student_ids = student_courses.mapped('student_id')
            else:
                faculty.student_ids = False

    @api.constrains('birth_date')
    def _check_birthdate(self):
        for record in self:
            if record.birth_date > fields.Date.today():
                raise ValidationError(_(
                    "Birth Date can't be greater than current date!"))

    @api.onchange('first_name', 'middle_name', 'last_name')
    def _onchange_name(self):
        if not self.middle_name:
            self.name = str(self.first_name) + " " + str(
                self.last_name)
        else:
            self.name = str(self.first_name) + " " + str(
                self.middle_name) + " " + str(self.last_name)

    def create_employee(self):
        for record in self:
            vals = {
                'name': record.name,
                'country_id': record.nationality.id,
                'gender': record.gender,
                'private_state_id': record.partner_id.id
            }
            emp_id = self.env['hr.employee'].create(vals)
            record.write({'emp_id': emp_id.id})
            record.partner_id.write({'partner_share': True, 'employee': True})

    @api.model
    def create(self, vals):
        """
        Overrides create to automatically link the user to the new faculty record.
        """
        res = super(OpFaculty, self).create(vals)
        if res.partner_id and res.partner_id.user_id:
            res.partner_id.user_id.faculty_id = res.id
        return res

    def write(self, vals):
        """
        Overrides write to update the user-faculty link if the partner is changed.
        It clears the faculty link from the old user and sets it on the new one.
        """
        # If partner is being changed, unlink the old user first
        if 'partner_id' in vals:
            for record in self:
                if record.partner_id and record.partner_id.user_id:
                    # Clear the faculty link from the user of the old partner
                    record.partner_id.user_id.faculty_id = False

        res = super(OpFaculty, self).write(vals)

        # After the write, link the new user
        if 'partner_id' in vals:
            for record in self:
                if record.partner_id and record.partner_id.user_id:
                    record.partner_id.user_id.faculty_id = record.id
        return res

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Faculties'),
            'template': '/tarcin_core/static/xls/op_faculty.xls'
        }]