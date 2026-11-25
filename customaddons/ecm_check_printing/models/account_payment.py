from odoo import _, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_vsg_print_checks(self):
        """Imprime los cheques propios emitidos en estos pagos."""
        checks = self.mapped("l10n_latam_new_check_ids").filtered(
            lambda c: c.payment_method_code == "own_checks"
        )
        if not checks:
            raise UserError(_("Los pagos seleccionados no tienen cheques propios que imprimir."))
        return checks.action_vsg_print_check()
