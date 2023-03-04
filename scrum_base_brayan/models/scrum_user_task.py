# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from .utils import *

from datetime import timedelta, timezone
from dateutil import tz


class ScrumUserTask(models.Model):
    _description = "User Task"
    _name = 'scrum.user.task'
    _inherit = ['mail.thread']
    # _inherit = ['ir.needaction_mixin', 'mail.thread']
    _order = 'priority , id desc'

    # @api.model
    # def _needaction_domain_get(self):
    #     return [('state', '!=', 'delivery')]

    name = fields.Char('Code', translate=True, default="New", copy=False)
    desc = fields.Char('Name', translate=True, size=100)

    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('5', '5'), ],
        string='Priority', default='3', copy=False)

    obs = fields.Text('How', translate=True, default="Obs")

    responsable_id = fields.Many2one('res.users', string='Responsable', copy=False)
    assigned_id = fields.Many2one('res.users', string='Who Assigned', copy=False)

    product_id = fields.Many2one('scrum.product', string='Product')
    project_company_id = fields.Many2one(related="product_id.project_id.company_id")

    story_id = fields.Many2one('scrum.user.story', string='User Story', domain="[('product_id', '=', product_id)]")
    process_id = fields.Many2one(comodel_name="scrum.process", string="Process")
    type_id = fields.Many2one(comodel_name="scrum.type", string="Type")
    sprint_id = fields.Many2one(comodel_name="scrum.sprint", string="Sprint")
    activity_control_ids = fields.One2many(comodel_name="scrum.activity.control", inverse_name="task_id", copy=False)

    settings_id = fields.Many2one(comodel_name="scrum.settings", compute="compute_settings_id")
    enable_analytic = fields.Boolean(related="settings_id.enable_analytic_account")
    enable_user = fields.Boolean(related="settings_id.able_to_modify_user")

    application_date = fields.Datetime('Application Date', default=fields.Datetime.now, copy=False)
    planned_date = fields.Datetime('Planned Date', copy=False)
    end_date = fields.Datetime('End Date', compute="compute_end_date", copy=False)
    real_init_date = fields.Datetime("Real Init date", readonly=True, copy=False)
    real_end_date = fields.Datetime("Real End date", readonly=True, copy=False)

    planned_hours = fields.Integer(string="Planned Hours")
    executed_hours = fields.Integer(string="Hours Executed", compute="compute_executed_hours")

    incidents_count = fields.Integer(compute="compute_incidents_count")

    state = fields.Selection([
        ('on_hold', 'On hold'),
        ('to_be_planned', 'To be planned'),
        ('assigned', 'Assigned'),
        ('doing', 'Doing'),
        ('test', 'Test'),
        ('returned', 'Returned'),
        ('qa', 'QA'),
        ('delivery', 'Delivery')],
        string='State', index=True, readonly=True, default='on_hold', copy=False)

    file_name = fields.Char("File", copy=False)
    file_01 = fields.Binary(
        string='File',
        copy=False,
        help='File')

    @api.depends('activity_control_ids')
    def compute_executed_hours(self):
        for rec in self:
            if rec.activity_control_ids:
                rec.executed_hours = sum(line.hours for line in rec.activity_control_ids)
            else:
                rec.executed_hours = None

    @api.onchange('story_id')
    def onchange_product_id(self):
        for rec in self:
            if rec.story_id:
                rec.product_id = rec.story_id.product_id

    @api.onchange('planned_date')
    def onchange_planned_date(self):
        for rec in self:
            if rec.planned_date and rec.application_date:
                if not is_work_day(rec.planned_date, rec):
                    msg = rec.planned_date.astimezone(tz.gettz(self.env.user.tz)).strftime('%Y-%m-%d %H:%M:%S')
                    rec.planned_date = None

                    return {
                        'warning': {
                            'title': "Error",
                            'message': _("Planned Date must be a labor day. %s is not working hours") % msg,
                        }}

                if rec.planned_date < rec.application_date:
                    rec.planned_date = None
                    return {
                        'warning': {
                            'title': "Error",
                            'message': _("Planned Date can't be less than application date"),
                        }}
                elif not rec.application_date:
                    rec.planned_date = None
                    return {
                        'warning': {
                            'title': "Error",
                            'message': "Application Date is Empty",
                        }}

    @api.depends('planned_hours', "planned_date")
    def compute_end_date(self):
        for record in self:
            if record.planned_date and record.planned_hours:
                total_apply_hours = 1

                planned_end_date = record.planned_date
                planned_day = planned_end_date.day
                planned_month = planned_end_date.month
                planned_year = planned_end_date.year

                while total_apply_hours <= record.planned_hours:
                    planned_end_date = planned_end_date + timedelta(hours=1)
                    week_day = planned_end_date.weekday()

                    current_day = planned_end_date.day
                    current_month = planned_end_date.month
                    current_year = planned_end_date.year

                    current_hour = planned_end_date.hour
                    current_minute = planned_end_date.minute
                    current_second = planned_end_date.second

                    if week_day != 5 and week_day != 6 and \
                            (
                                    (
                                            (current_minute == 0 and current_second == 0) and
                                            (
                                                    (
                                                            (planned_day == current_day) and
                                                            (planned_month == current_month) and
                                                            (planned_year == current_year) and
                                                            (
                                                                    (13 <= current_hour <= 17) or
                                                                    (19 <= current_hour <= 22)
                                                            )
                                                    ) or
                                                    (
                                                            (planned_day != current_day) and
                                                            (
                                                                    (13 < current_hour <= 17) or
                                                                    (19 <= current_hour <= 22)
                                                            )
                                                    )
                                            )
                                    ) or
                                    (
                                            (current_minute != 0 or current_second != 0) and
                                            (
                                                    (13 <= current_hour < 17) or
                                                    (18 <= current_hour < 22)
                                            )
                                    )
                            ):
                        total_apply_hours += 1

                record.end_date = planned_end_date
            else:
                record.end_date = False

    @api.depends('product_id')
    def compute_settings_id(self):
        if self.product_id:
            setting_obj = self.env['scrum.settings'].search([
                ('company_id.name', '=', self.project_company_id.name)]
            )

            if not setting_obj:
                self.settings_id = False
                raise UserError("No exists Settings for this company: {}".format(self.project_company_id.name))
            else:
                self.settings_id = setting_obj
        else:
            self.settings_id = False

    def compute_incidents_count(self):
        for record in self:
            record.incidents_count = self.env["scrum.user.bug"].search_count([('task_id', "=", self.id)])

    def action_view_incident(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Incidents',
            'view_mode': 'tree,form',
            'res_model': 'scrum.user.bug',
            'domain': [('task_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def exe_be_planned(self):
        for record in self:
            record.state = 'to_be_planned'
            record.message_post(body=_("To be pĺanned to : %s") % record.responsable_id.name)

    def exe_assigned(self):
        if not self.responsable_id:
            raise UserError(_('You need a Responsable'))
        for record in self:
            record.state = 'assigned'
            record.sudo().assigned_id = record.env.user
            record.message_post(body=_("Assigned to : %s") % record.responsable_id.name)

    def exe_i_want(self):
        for record in self:
            record.sudo().state = 'assigned'
            record.sudo().responsable_id = record.env.user
            record.sudo().assigned_id = record.env.user
            record.sudo().message_post(body=_("Assigned to : %s") % record.env.user.name)

    def exe_doing(self):
        for record in self:
            record.state = 'doing'
            record.message_post(body=_("Doing: %s") % record.env.user.name)
            record.real_init_date = fields.Datetime.now()

    def exe_test(self):
        for record in self:
            record.state = 'test'
            record.message_post(body=_("Test: %s") % record.env.user.name)

    def exe_qa(self):
        for record in self:
            record.state = 'qa'

    def exe_delivery(self):
        for record in self:
            record.state = 'delivery'
            record.message_post(body=_("Delivery: %s") % record.env.user.name)
            record.real_end_date = fields.Datetime.now()

    def exe_open(self):
        for record in self:
            record.state = 'on_hold'
            record.message_post(body=_("To Be planned: %s") % record.env.user.name)

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('scrum.user.task') or "New"
        return super(ScrumUserTask, self).create(vals)

    def name_get(self):
        res = super(ScrumUserTask, self).name_get()
        result = []
        for element in res:
            product_id = element[0]
            code = self.browse(product_id).name
            desc = self.browse(product_id).desc
            name = code and '[%s] %s' % (code, desc) or '%s' % desc
            result.append((product_id, name))
        return result
