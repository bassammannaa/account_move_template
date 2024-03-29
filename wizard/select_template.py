# -*- coding: utf-8 -*-
# Copyright 2015-2017 See manifest
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api
import time


class WizardSelectMoveTemplate(models.TransientModel):
    _name = "wizard.select.move.template"

    template_id = fields.Many2one('account.move.template', required=True)
    partner_id = fields.Many2one('res.partner', 'Partner')
    line_ids = fields.One2many('wizard.select.move.template.line', 'template_id')
    state = fields.Selection([('template_selected', 'Template selected')], 'State')

    @api.multi
    def load_lines(self):
        self.ensure_one()
        lines = self.template_id.template_line_ids
        for line in lines.filtered(lambda l: l.type == 'input'):
            self.env['wizard.select.move.template.line'].create({
                'template_id': self.id,
                'sequence': line.sequence,
                'name': line.name,
                'amount': 0.0,
                'account_id': line.account_id.id,
                'employee': line.employee.id,
                'office_branch': line.office_branch.id,
                'account_items': line.account_items.id,
                'application_id': line.application_id.id,
                'move_line_type': line.move_line_type,
                'partner_id': line.partner_id.id,
            })
        if not self.line_ids:
            return self.load_template()
        self.state = 'template_selected'
        view_rec = self.env.ref('account_move_template.wizard_select_template')
        return {
            'view_type': 'form',
            'view_id': [view_rec.id],
            'view_mode': 'form',
            'res_model': 'wizard.select.move.template',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context,
        }

    @api.multi
    def load_template(self):
        self.ensure_one()

        input_lines = {}
        partners_lines = {}
        employee_lines = {}
        office_branchs_lines = {}
        account_items_lines = {}
        applications_lines = {}
        for template_line in self.line_ids:
            input_lines[template_line.sequence] = template_line.amount
            partners_lines[template_line.sequence] = template_line.partner_id.id
            employee_lines[template_line.sequence] = template_line.employee.id
            office_branchs_lines[template_line.sequence] = template_line.office_branch.id
            applications_lines[template_line.sequence] = template_line.application_id.id
            account_items_lines[template_line.sequence] = template_line.account_items.id

        amounts = self.template_id.compute_lines(input_lines)
        name = self.template_id.name
        journal = self.template_id.journal_id.id

        move = self._create_move(name, journal)
        lines = []
        for line in self.template_id.template_line_ids:
            lines.append((0, 0, self._prepare_line(line, amounts, journal, partners_lines, employee_lines, office_branchs_lines,
                                                   applications_lines, account_items_lines)))

        move.write({'line_ids': lines})



        # partner = self.partner_id.id
        # moves = self.env['account.move']
        # for journal in self.template_id.template_line_ids.mapped('journal_id'):
        #     lines = []
        #
        #     move = self._create_move(name, journal.id, partner)
        #     moves = moves + move
        #     for line in self.template_id.template_line_ids.filtered(
        #             lambda j: j.journal_id == journal):
        #         lines.append((0, 0,
        #                       self._prepare_line(line, amounts, partner)))
        #     move.write({'line_ids': lines})

        return {
            'domain': [('id', 'in', move.ids)],
            'name': 'Entries from template: %s' % name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.model
    def _create_move(self, ref, journal_id):
        return self.env['account.move'].create({
            'ref': ref,
            'journal_id': journal_id,
        })

    @api.model
    def _prepare_line(self, line, amounts, journal_id, partners_lines, employee_lines, office_branchs_lines, applications_lines, account_items_lines):
        debit = line.move_line_type == 'dr'
        values = {
            'name': line.name,
            'journal_id': journal_id,
            'analytic_account_id': line.analytic_account_id.id,
            'account_id': line.account_id.id,
            'employee': employee_lines[line.sequence],
            'office_branch': office_branchs_lines[line.sequence],
            'account_items': account_items_lines[line.sequence],
            'application_id': applications_lines[line.sequence],
            'date': time.strftime('%Y-%m-%d'),
            'credit': not debit and amounts[line.sequence] or 0.0,
            'debit': debit and amounts[line.sequence] or 0.0,
            'partner_id': partners_lines[line.sequence],
        }
        return values


class WizardSelectMoveTemplateLine(models.TransientModel):
    _description = 'Template Lines'
    _name = "wizard.select.move.template.line"

    template_id = fields.Many2one(
        'wizard.select.move.template')
    sequence = fields.Integer(required=True)
    name = fields.Char(required=True, readonly=True)
    account_id = fields.Many2one(
        'account.account', required=True, readonly=True)
    move_line_type = fields.Selection(
        [('cr', 'Credit'), ('dr', 'Debit')], required=True, readonly=True)
    amount = fields.Float(required=True)
    employee = fields.Many2one('hr.employee', string='Staff Name', required=False, )
    office_branch = fields.Many2one('housemaid.configuration.officebranches',
                                    string='Office Branch', required=False, )
    application_id = fields.Many2one('housemaid.applicant.applications',
                                     string="Housemaid Ref", required=False)
    partner_id = fields.Many2one('res.partner', 'Partner')
    account_items = fields.Many2one('housemaid.configuration.accountitems',
                                    string='Account Item', required=False, )


