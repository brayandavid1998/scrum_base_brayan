# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

class ScrumNotes(models.Model):
    _description = "Scrum Notes"
    _name = 'scrum.notes'
    _inherit = ['mail.thread']
    # _inherit = ['ir.needaction_mixin', 'mail.thread']
    _order = 'id desc'

    # @api.model
    # def _needaction_domain_get(self):
    #     return [('name', '!=', '')]

    name = fields.Char('Code', translate=True, default="New")
    desc = fields.Char('Name', translate=True, size=100)
    obs = fields.Text('Notes', translate=True)
    date = fields.Datetime('Date', default=fields.Datetime.now)



    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('scrum.notes') or "New"
        return super(ScrumNotes, self).create(vals)


    def name_get(self):
        res = super(ScrumNotes, self).name_get()
        result = []
        for element in res:
            product_id = element[0]
            code = self.browse(product_id).name
            desc = self.browse(product_id).desc
            name = code and '[%s] %s' % (code, desc) or '%s' % desc
            result.append((product_id, name))
        return result