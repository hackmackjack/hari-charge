from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    faculty_id = fields.Many2one('op.faculty', string="Faculty", help="The faculty record associated with this user.")