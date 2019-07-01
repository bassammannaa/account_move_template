# -*- coding: utf-8 -*-
# Copyright 2015-2017 See manifest
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api


class AccountMoveTemplate(models.Model):
    _name = 'account.move.template'
    _inherit = ['account.document.template',
                # 'mail.activity.mixin',  TODO:  uncomment for saas-15
                'mail.thread']

    @api.model
    def _company_get(self):
        return self.env['res.company']._company_default_get(object='account.move.template')

    company_id = fields.Many2one('res.company', required=True, change_default=True, default=_company_get,)
    journal_id = fields.Many2one('account.journal', required=True, domain=[('type', '=', 'general')], )
    template_line_ids = fields.One2many('account.move.template.line', inverse_name='template_id',)

    @api.multi
    def action_run_template(self):
        self.ensure_one()
        action = self.env.ref(
            'account_move_template.action_wizard_select_template').read()[0]
        action.update({'context': {'default_template_id': self.id}})
        return action


class AccountMoveTemplateLine(models.Model):
    _name = 'account.move.template.line'
    _inherit = 'account.document.template.line'

    journal_id = fields.Many2one('account.journal')
    account_id = fields.Many2one('account.account',required=True,ondelete="cascade")
    move_line_type = fields.Selection([('cr', 'Credit'), ('dr', 'Debit')], required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', ondelete="cascade")
    template_id = fields.Many2one('account.move.template')
    employee = fields.Many2one('hr.employee', string='Staff Name', required=False, )
    office_branch = fields.Many2one('housemaid.configuration.officebranches',
                                    string='Office Branch', required=False, )
    application_id = fields.Many2one('housemaid.applicant.applications',
                                     string="Housemaid Ref", required=False)
    partner_id = fields.Many2one('res.partner', 'Partner')
    account_items = fields.Many2one('housemaid.configuration.accountitems',
                                    string='Account Items', required=False, )

    _sql_constraints = [
        ('sequence_template_uniq', 'unique (template_id,sequence)',
         'The sequence of the line must be unique per template !')
    ]


class AccountMoveLineLists(models.Model):
    _name = 'account.move.line'
    _inherit = 'account.move.line'
    _description = 'Journal Item Lists'

    employee = fields.Many2one('hr.employee', string='Staff Name', ondelete='restrict',)
    office_branch = fields.Many2one('housemaid.configuration.officebranches',
                                    string='Office Branch', ondelete='restrict',)
    application_id = fields.Many2one('housemaid.applicant.applications',
                                     string="Housemaid Ref", ondelete='restrict', )
    account_items = fields.Many2one('housemaid.configuration.accountitems',
                                    string='Account Items', required=False, )

