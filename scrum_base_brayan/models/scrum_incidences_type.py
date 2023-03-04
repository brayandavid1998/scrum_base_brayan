from odoo import fields, models, api


class ScrumIncidencesType(models.Model):
    _name = 'scrum.incidences.type'
    _description = 'Types'

    name = fields.Char(string="Name")
    code = fields.Integer(string="Code")
    is_rq_affected = fields.Boolean(string="Affect Requirement", default=False)


