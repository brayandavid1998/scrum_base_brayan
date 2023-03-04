from odoo import fields, models, api


class ScrumActivityControl(models.Model):
    _name = 'scrum.activity.control'
    _description = 'Activity Control'

    description = fields.Text(string="Description")
    hours = fields.Float(string="Hour")
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
    )
    date = fields.Date(string="Date")

    user_id = fields.Many2one(comodel_name="res.users", string="User", default=lambda self: self.env.user)
    task_id = fields.Many2one(comodel_name="scrum.user.task", string="Requirement",)
    bug_id = fields.Many2one(comodel_name="scrum.user.bug", string="Incidence")
