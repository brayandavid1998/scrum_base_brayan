# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError


class ProjectTag(models.Model):
    _name = 'project.tag'
    _description = 'Project Tags'

    active = fields.Boolean(default=True)
    color = fields.Integer(required=True, default=0)
    name = fields.Char(required=True)


class ScrumProject(models.Model):
    _description = "Scrum Project"
    _name = 'scrum.project'
    _inherit = ['mail.thread']
    # _inherit = ['ir.needaction_mixin', 'mail.thread']
    _order = 'id desc'

    # @api.model
    # def _needaction_domain_get(self):
    #     return [('state', '!=', 'done')]

    name = fields.Char('Code', translate=True, default="New")
    desc = fields.Char('Name', translate=True, size=100)
    obs = fields.Text('Notes', translate=True)
    tag_ids = fields.Many2many('project.tag', string='Tags')

    partner_id = fields.Many2one('res.partner', string='Partner')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    entry_date = fields.Datetime('Date', default=fields.Datetime.now)
    end_date = fields.Datetime('End Date')

    state = fields.Selection([
        ('to_do', 'To Do'),
        ('doing', 'Doing'),
        ('done', 'Done')],
        string='State', index=True, readonly=True, default='to_do', copy=False)

    product_count = fields.Integer('Product', compute="_get_product_count")
    product_ids = fields.One2many('scrum.product', 'project_id', 'Product')
    stories_count = fields.Integer('User stories', compute="compute_stories_count")
    stories_ids = fields.One2many(comodel_name='scrum.user.story', inverse_name='product_id')
    task_count = fields.Integer("Requirements", compute="compute_task_count")
    bug_count = fields.Integer(compute="compute_bug_count")

    image_medium = fields.Binary(
        "Medium-sized image",
        help="Product image")

    # planned_percent = fields.Float('Planned Percent', compute="_compute_percents")
    # executed_percent = fields.Float('Executed Percent', compute="_compute_percents")

    def _set_image_medium(self):
        for rec in self:
            rec._set_image_value(self.image_medium)

    def compute_bug_count(self):
        for rec in self:
            rec.bug_count = self.env["scrum.user.bug"].search_count(
                [('product_id', "in", self.product_ids.ids)]
            )
    """
    def _compute_percents(self):
        for rec in self:
            products = self.env['scrum.product'].search([('project_id', '=', rec.id)])

            planned_percent = 0
            executed_percent = 0
            for product in products:
                planned_percent += product.planned_percent
                executed_percent += product.executed_percent
    """
    @api.depends('stories_ids')
    def compute_stories_count(self):
        for record in self:
            record.stories_count = len(record.stories_ids)

    def compute_task_count(self):
        for record in self:
            record.task_count = self.env['scrum.user.task'].search_count(
                [('product_id', 'in', self.product_ids.ids)]
            )

    @api.depends('product_ids')
    def _get_product_count(self):
        for project in self:
            project.product_count = len(project.product_ids)

    def action_view_user_bug(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Incident',
            'view_mode': 'tree,form',
            'res_model': 'scrum.user.bug',
            'domain': [('product_id', "in", self.product_ids.ids)],
            'context': "{'create': False}"
        }

    def action_view_user_stories(self):
        stories = self.mapped('stories_ids')
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'User stories',
            'view_mode': 'tree,form',
            'res_model': 'scrum.user.story',
            'domain': [('id', 'in', stories.ids)],
            'context': "{'create': False}"
        }

    def action_view_user_task(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Requirements',
            'view_mode': 'tree,form',
            'res_model': 'scrum.user.task',
            'domain':  [('product_id', 'in', self.product_ids.ids)],
            'context': "{'create': False}"
        }

    def action_view_products(self):
        products = self.mapped('product_ids')
        action = self.env.ref('scrum_base.action_scrum_product').read()[0]
        if len(products) > 0:
            action['domain'] = [('id', 'in', products.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

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
            vals['name'] = self.env['ir.sequence'].next_by_code('scrum.project') or "New"
        return super(ScrumProject, self).create(vals)

    def name_get(self):
        res = super(ScrumProject, self).name_get()
        result = []
        for element in res:
            project_id = element[0]
            code = self.browse(project_id).name
            desc = self.browse(project_id).desc
            name = code and '[%s] %s' % (code, desc) or '%s' % desc
            result.append((project_id, name))
        return result