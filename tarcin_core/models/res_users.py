from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    faculty_id = fields.Many2one(
        'op.faculty', string='Related Faculty',
        compute='_compute_faculty_id', store=True)

    @api.depends('partner_id')
    def _compute_faculty_id(self):
        for user in self:
            faculty = self.env['op.faculty'].search([
                ('partner_id', '=', user.partner_id.id)], limit=1)
            user.faculty_id = faculty or False