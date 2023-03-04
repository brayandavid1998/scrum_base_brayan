# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

class ScrumUserStory(models.Model):
    _description = "User Story"
    _name = 'scrum.user.story'
    _inherit = ['mail.thread']
    # _inherit = ['ir.needaction_mixin', 'mail.thread']
    _order = 'id desc'

    # @api.model
    # def _needaction_domain_get(self):
    #     return [('state', '!=', 'done')]

    name = fields.Char('Code', translate=True, default="New", copy=False)
    desc = fields.Char('Name', translate=True, size=100)

    obs_how = fields.Text('How', translate=True , default="How")
    obs_want = fields.Text('Want', translate=True, default="Want")
    obs_for = fields.Text('For', translate=True, default="For")
    obs_terms = fields.Text('Terms', translate=True, default="Term")

    responsable_id = fields.Many2one('res.partner', string='Responsable')
    product_id = fields.Many2one('scrum.product', string='Product')

    entry_date = fields.Datetime('Date', default=fields.Datetime.now, copy=False)
    end_date = fields.Datetime('End Date', copy=False)

    task_count = fields.Integer(compute="compute_task_count")
    bug_count = fields.Integer(compute="compute_bug_count")

    state = fields.Selection([
        ('to_do', 'To Do'),
        ('doing', 'Doing'),
        ('done', 'Done')],
        string='State', index=True, readonly=True, default='to_do', copy=False)

    file_name = fields.Char("File", copy=False)
    file_01 = fields.Binary(
        string='File',
        copy=False,
        help='File')

    def compute_bug_count(self):
        for record in self:
            record.bug_count = self.env['scrum.user.bug'].search_count(
                [('product_id', '=', self.product_id.id)]
            )

    def action_view_bug(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Incident',
            'view_mode': 'tree,form',
            'res_model': 'scrum.user.bug',
            'domain': [('product_id', '=', self.product_id.id)],
            'context': "{'create': False}"
        }

    def compute_task_count(self):
        for record in self:
            record.task_count = self.env['scrum.user.task'].search_count(
                [('story_id', '=', self.id)])

    def action_view_requirement(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Requirements',
            'view_mode': 'tree,form',
            'res_model': 'scrum.user.task',
            'domain': [('story_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def exe_doing(self):
        for record in self:
            record.state = 'doing'
            record.message_post(body=_("Doing: %s") % record.env.user.name)

    def exe_done(self):
        for record in self:
            record.state = 'done'
            record.message_post(body=_("Done: %s") % record.env.user.name)
            record.end_date = fields.Datetime.now()

    def exe_open(self):
        for record in self:
            record.state = 'to_do'
            record.message_post(body=_("To Do: %s") % record.env.user.name)

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('scrum.user.story') or "New"
        return super(ScrumUserStory, self).create(vals)

    def name_get(self):
        res = super(ScrumUserStory, self).name_get()
        result = []
        for element in res:
            product_id = element[0]
            code = self.browse(product_id).name
            desc = self.browse(product_id).desc
            name = code and '[%s] %s' % (code, desc) or '%s' % desc
            result.append((product_id, name))
        return result
