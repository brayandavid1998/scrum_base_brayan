from odoo import fields, models, api
from odoo.exceptions import UserError


class ScrumSettings(models.Model):
    _name = 'scrum.settings'
    _description = 'Settings'
    _rec_name = "company_id"

    enable_analytic_account = fields.Boolean(string="Enable analytic account", default=False)
    able_to_modify_user = fields.Boolean(string="Able to modify user", default=False)

    company_id = fields.Many2one(comodel_name="res.company", defauul="default_company_name", required=True)

    def default_company_name(self):
        for record in self:
            return record.env.company

    @api.model
    def create(self, vals_list):
        is_company_create = self.search([('company_id', '=', vals_list.get('company_id'))])
        if is_company_create:
            raise UserError("Cannot create settings for this company: {}. Already exists".format(
                is_company_create.company_id.name)
            )
        else:
            obj = super(ScrumSettings, self).create(vals_list)
            return obj
