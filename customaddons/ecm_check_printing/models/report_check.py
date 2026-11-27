from odoo import api, models


class ReportVsgCheck(models.AbstractModel):
    """Contexto del reporte del cheque.

    Existe para que las opciones elegidas en el asistente lleguen siempre
    definidas a la plantilla: QWeb falla al leer un nombre que no existe, y
    ``data`` viene vacio cuando el reporte se lanza desde el menu de acciones.
    """

    _name = "report.ecm_check_printing.report_vsg_check"
    _description = "Cheque: contexto del reporte"

    @api.model
    def _vsg_docids(self, docids):
        """Los ids del reporte, vengan por donde vengan.

        Cuando la accion lleva ``data``, el cliente web pide
        ``/report/pdf/<reporte>`` SIN ids y los manda en el contexto como
        ``active_ids`` (ver addons/web/controllers/report.py, rama 'Particular
        report'). Mirar solo ``docids`` deja el reporte sin registros y sale
        una hoja en blanco.
        """
        return list(docids or self.env.context.get("active_ids") or [])

    @api.model
    def _get_report_values(self, docids, data=None):
        docids = self._vsg_docids(docids)
        checks = self.env["l10n_latam.check"].browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": "l10n_latam.check",
            "docs": checks,
            "vsg_options": {check.id: check._vsg_options(data) for check in checks},
        }
