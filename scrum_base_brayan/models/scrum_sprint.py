from odoo import fields, models, api


class ScrumSprint(models.Model):
    _name = 'scrum.sprint'
    _description = 'Sprint'

    name = fields.Char(String="Name")

    process_id = fields.Many2one(comodel_name="scrum.process", string="Process")
    initial_sprint = fields.Date(string="Initial")
    end_sprint = fields.Date(string="End")
