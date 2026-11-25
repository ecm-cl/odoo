from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit='account.move'

    x_native_candidate=fields.Char(copy=False,index=True)
    x_native_folio=fields.Char(string='Folio tributario original',copy=False,index=True)
    x_native_label=fields.Char(string='Número',compute='_compute_native_label',store=True,index=True)
    x_native_evidence=fields.Text(string='Identificación y evidencia',copy=False)
    x_note_origin_ref=fields.Char(string='Factura referenciada',copy=False)
    x_native_special_accounts=fields.Boolean(copy=False)
    x_legacy_duplicate=fields.Boolean(string='Duplicación contable heredada',copy=False)

    @api.depends('name','move_type','x_native_candidate','x_native_folio',
                 'partner_id.vat','l10n_latam_document_type_id')
    def _compute_native_label(self):
        for move in self:
            if move.x_native_candidate and move.move_type in ('in_invoice','in_refund'):
                t=move.l10n_latam_document_type_id
                move.x_native_label=f'{t.doc_code_prefix} ({t.code}) COMPRA / {move.partner_id.vat} / {move.x_native_folio}'
            else:move.x_native_label=move.name

    @api.depends('x_native_label')
    def _compute_display_name(self):
        super()._compute_display_name()
        for move in self.filtered(lambda m:m.x_native_candidate and m.move_type in ('in_invoice','in_refund')):
            move.display_name=move.x_native_label

    def _update_sequence_made_gap(self,invalidate_current=False):
        purchases=self.filtered(lambda m:m.journal_id.type=='purchase' and m.l10n_latam_use_documents)
        super(AccountMove,self-purchases)._update_sequence_made_gap(invalidate_current)
        purchases.made_sequence_gap=False

    def _compute_payments_widget_to_reconcile_info(self):
        super()._compute_payments_widget_to_reconcile_info()
        for move in self:
            widget=move.invoice_outstanding_credits_debits_widget
            if not widget:continue
            content=[]
            for item in widget['content']:
                line=self.env['account.move.line'].browse(item['id'])
                if line.x_reserved_document_id and line.x_reserved_document_id!=move:continue
                if line.x_reserved_reference and line.x_reserved_document_id!=move:continue
                content.append(item)
            move.invoice_outstanding_credits_debits_widget={**widget,'content':content} if content else False

class AccountMoveLine(models.Model):
    _inherit='account.move.line'
    x_reserved_document_id=fields.Many2one('account.move',copy=False,index=True,check_company=True)
    x_reserved_reference=fields.Char(string='Aplicación documental Flex',copy=False,index=True)

    @api.constrains('account_id','display_type')
    def _check_payable_receivable(self):
        # Exact historical reclassifications and non-trade receivables/provisions.
        special=self.filtered(lambda l:l.move_id.x_native_special_accounts
            and l.x_legacy_cuenta==l.account_id.code
            and ((l.display_type=='payment_term' and l.account_id.code in ('1106002','2102097'))
                 or (l.display_type=='product' and l.account_id.code=='1104003')))
        return super(AccountMoveLine,self-special)._check_payable_receivable()
