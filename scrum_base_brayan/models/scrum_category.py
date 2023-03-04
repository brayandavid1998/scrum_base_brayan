from odoo import fields, models, api


class SScrumCategory(models.Model):
    _name = 'scrum.category'
    _description = 'Categories'

    name = fields.Char(string="Name",)
    code = fields.Integer(string="Code")
    abbreviation = fields.Char(string="Initials", size=5)
