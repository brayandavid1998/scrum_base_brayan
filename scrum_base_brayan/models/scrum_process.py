from odoo import fields, models, api


class ScrumProcess(models.Model):
    _name = 'scrum.process'
    _description = 'Process'

    name = fields.Char(string="Name")
    code = fields.Integer(string="Code")
    abbreviation = fields.Char(string="abbreviation", size=5)

