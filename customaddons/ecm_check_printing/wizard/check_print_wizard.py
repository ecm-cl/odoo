from urllib.parse import urlencode

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class VsgCheckPrintWizard(models.TransientModel):
    """Opciones que el administrativo elige antes de imprimir un cheque.

    El tipo de cheque y el cruzado no son propiedades del cheque en Odoo: se
    deciden en el momento de llenarlo. Por eso viven aquí y no en
    ``l10n_latam.check``; el diario solo aporta el valor con el que se abre el
    dialogo.
    """

    _name = "vsg.check.print.wizard"
    _description = "Impresión de cheques: opciones"

    check_ids = fields.Many2many(
        "l10n_latam.check", string="Cheques", required=True)
    endorsement = fields.Selection(
        [("nominativo", "Nominativo"),
         ("orden", "A la orden"),
         ("portador", "Al portador")],
        string="Tipo de cheque", required=True, default="nominativo",
        help="Nominativo tacha 'a la orden de' y 'o al portador'. "
             "A la orden tacha solo 'o al portador'. "
             "Al portador no tacha nada.",
    )
    crossed = fields.Boolean(
        string="Cruzado",
        help="Imprime las dos rayas paralelas: el cheque solo se puede "
             "depositar en cuenta, no cobrar por caja.",
    )
    year_prefix = fields.Boolean(
        string="Imprimir el '20' del año",
        help="Apagar cuando el formulario del banco ya trae impreso el '20' y "
             "solo quedan libres los dos últimos casilleros.",
    )

    sheet = fields.Selection(
        [("cheque", "Hoja del cheque"),
         ("carta", "Hoja carta, para calibrar a contraluz")],
        string="Hoja", required=True, default="cheque",
        help="La hoja del cheque se gira para entrar por el lado corto. "
             "La hoja carta imprime lo mismo sin girar, apoyado en la esquina "
             "superior izquierda, para compararlo contra un cheque real.",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        ids = self.env.context.get("default_check_ids") or []
        journal = self.env["l10n_latam.check"].browse(ids)[:1].payment_id.journal_id
        if journal:
            res.setdefault(
                "endorsement", journal.vsg_check_endorsement_default or "nominativo")
            res.setdefault("crossed", journal.vsg_check_crossed_default)
            res.setdefault("year_prefix", not journal.vsg_check_year_preprinted)
        return res

    def _vsg_data(self):
        """Opciones en la forma en que las lee el reporte."""
        self.ensure_one()
        return {
            "vsg_endorsement": self.endorsement,
            "vsg_crossed": self.crossed,
            "vsg_year_prefix": self.year_prefix,
        }

    def _vsg_checks(self):
        self.ensure_one()
        if not self.check_ids:
            raise UserError(_("No hay cheques que imprimir."))
        return self.check_ids

    def action_print(self):
        """Abre el dialogo de impresión del sistema con el cheque ya cargado."""
        self.ensure_one()
        params = urlencode({
            "ids": ",".join(str(i) for i in self._vsg_checks().ids),
            "endorsement": self.endorsement,
            "crossed": "1" if self.crossed else "0",
            "year_prefix": "1" if self.year_prefix else "0",
            "sheet": self.sheet,
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/vsg_check_printing/print?%s" % params,
            "target": "new",
        }
