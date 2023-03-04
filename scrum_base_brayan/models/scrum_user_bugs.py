# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

class ScrumUserBugs(models.Model):
    _description = "Developer Bugs"
    _name = 'scrum.user.bug'
    _inherit = ['mail.thread']
    # _inherit = ['ir.needaction_mixin', 'mail.thread']
    _order = 'id desc'

    # @api.model
    # def _needaction_domain_get(self):
    #     return [('state', '!=', 'delivery')]

    name = fields.Char('Code', translate=True, default="New", copy=False)
    desc = fields.Char('Name', translate=True, size=100)
    difficulty = fields.Integer('Difficulty', size=100)
    obs = fields.Text('How', translate=True , default="Obs")

    developer_id = fields.Many2one('res.users', string='Responsable')
    product_id = fields.Many2one('scrum.product', string='Product')
    project_company_id = fields.Many2one(related="product_id.project_id.company_id")
    process_id = fields.Many2one(comodel_name="scrum.process", string="Process")
    task_id = fields.Many2one('scrum.user.task', string='Task', domain="[('product_id', '=', product_id)]")
    incidence_type_id = fields.Many2one(comodel_name="scrum.incidences.type", copy=False)
    is_required = fields.Boolean(related="incidence_type_id.is_rq_affected")
    activity_control_ids = fields.One2many(comodel_name="scrum.activity.control",
                                           inverse_name="bug_id", copy=False)
    settings_id = fields.Many2one(comodel_name="scrum.settings", compute="compute_settings_id")
    enable_analytic_account = fields.Boolean(related="settings_id.enable_analytic_account")
    enable_user = fields.Boolean(related="settings_id.able_to_modify_user")
    sprint_id = fields.Many2one(comodel_name="scrum.sprint", string="Sprint")

    entry_date = fields.Datetime('Date', default=fields.Datetime.now, copy=False)
    end_date = fields.Datetime('End Date', copy=False)

    planned_hours = fields.Integer(string="Planned Hours")
    executed_hours = fields.Integer(string="Hours Executed", compute="compute_executed_hours")

    state = fields.Selection([
        ('on_hold', 'On hold'),  # to_do
        ('to_be_planned', 'To be planned'),  # new
        ('assigned', 'Assigned'),
        ('doing', 'Doing'),  # doing
        ('test', 'Test'),  # new (done)
        ('returned', 'Returned'),  # returned
        ('qa', 'QA'),  # qa
        ('delivery', 'Delivery')],  # delivery
        string='State', index=True, readonly=True, default='on_hold', copy=False)

    @api.depends('product_id')
    def compute_settings_id(self):
        if self.product_id:
            self.settings_id = self.env['scrum.settings'].search([
                ('company_id.name', '=', self.project_company_id.name)]
            )
        else:
            self.settings_id = False

    @api.depends('activity_control_ids')
    def compute_executed_hours(self):
        for rec in self:
            if rec.activity_control_ids:
                rec.executed_hours = sum(line.hours for line in rec.activity_control_ids)
            else:
                rec.executed_hours = None

    def exe_be_planned(self):
        for record in self:
            record.state = 'to_be_planned'
            record.message_post(body=_("To be Planned: %s") % record.env.user.name)

    def exe_assigned(self):
        for record in self:
            record.state = 'assigned'
            record.message_post(body=_("Assigned: %s") % record.env.user.name)

    def exe_doing(self):
        for record in self:
            record.state = 'doing'
            record.message_post(body=_("Doing: %s") % record.env.user.name)

    def exe_test(self):
        for record in self:
            record.state = 'test'
            record.message_post(body=_("Done: %s") % record.env.user.name)
            # record.end_date = fields.Datetime.now()

    def exe_return(self):
        for record in self:
            record.state = 'returned'
            record.message_post(body=_("Returned: %s") % record.env.user.name)
            # record.end_date = fields.Datetime.now()

    def exe_qa(self):
        for record in self:
            record.state = 'qa'
            record.message_post(body=_("QA: %s") % record.env.user.name)
            # record.end_date = fields.Datetime.now()

    def exe_delivery(self):
        for record in self:
            record.state = 'delivery'
            record.message_post(body=_("Delivery: %s") % record.env.user.name)
            record.end_date = fields.Datetime.now()

    def exe_open(self):
        for record in self:
            record.state = 'on_hold'
            record.message_post(body=_("On hold: %s") % record.env.user.name)

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('scrum.user.bug') or "New"
        obj_incidence_id = self.env['scrum.incidences.type'].sudo().browse(vals.get('incidence_type_id'))
        if obj_incidence_id.is_rq_affected:
            obj_task_id = self.env['scrum.user.task'].sudo().browse(vals.get('task_id'))
            obj_task_id.update({'state': 'returned'})
        return super(ScrumUserBugs, self).create(vals)

    file_name = fields.Char("File")
    file_01 = fields.Binary(
        string='File',
        copy=False,
        help='File')

    def name_get(self):
        res = super(ScrumUserBugs, self).name_get()
        result = []
        for element in res:
            product_id = element[0]
            code = self.browse(product_id).name
            desc = self.browse(product_id).desc
            name = code and '[%s] %s' % (code, desc) or '%s' % desc
            result.append((product_id, name))
        return result