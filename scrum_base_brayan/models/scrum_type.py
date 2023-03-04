from odoo import fields, models, api


class ScrumType(models.Model):
    _name = 'scrum.type'
    _description = 'Type'

    name = fields.Char(string="Name", translate=True)
    code = fields.Integer(string="Code")
    abbreviation = fields.Char(string="abbreviation", size=5)

