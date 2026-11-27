import io

from odoo import models
from odoo.tools.pdf import (
    ArrayObject, NameObject, NumberObject, PdfFileReader, PdfFileWriter, generic,
)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _vsg_check_reports(self):
        """Los reportes que se imprimen sobre el formulario del banco."""
        reportes = self.env["ir.actions.report"]
        for xmlid in ("ecm_check_printing.action_report_vsg_check",
                      "ecm_check_printing.action_report_vsg_check_calibration"):
            reportes |= self.env.ref(xmlid, raise_if_not_found=False) \
                or self.env["ir.actions.report"]
        return reportes

    def get_paperformat(self):
        """Permite imprimir el mismo cheque sobre una hoja carta.

        Es lo que se pone a contraluz contra un cheque real para calibrar: el
        contenido queda en el mismo lugar respecto de la esquina superior
        izquierda, pero sobre un papel que si entra en cualquier impresora.
        """
        if self.env.context.get("vsg_check_letter") and self in self._vsg_check_reports():
            carta = self.env.ref(
                "ecm_check_printing.paperformat_vsg_check_letter",
                raise_if_not_found=False)
            if carta:
                return carta
        return super().get_paperformat()

    def _vsg_journal_of(self, report, res_ids):
        """Diario que manda sobre la hoja de este reporte.

        Cuando la accion lleva ``data``, el cliente web pide el reporte sin
        ids en la URL y los manda en el contexto como ``active_ids``. Sin
        mirar ahi, este metodo no encuentra diario y la pagina sale sin girar.
        """
        if isinstance(res_ids, int):
            res_ids = [res_ids]
        res_ids = list(res_ids or self.env.context.get("active_ids") or [])
        if not res_ids:
            return self.env["account.journal"]
        record = self.env[report.model].browse(res_ids[:1])
        return record if report.model == "account.journal" \
            else record.payment_id.journal_id

    def _vsg_sheet_is_vertical(self, journal):
        """El diario decide si la hoja entra por el lado corto."""
        if self.env.context.get("vsg_check_letter"):
            # sobre hoja carta se imprime sin girar: la hoja ya entra por el
            # lado largo y lo que importa es la esquina de referencia
            return False
        return bool(journal and journal.vsg_check_sheet_vertical)

    @staticmethod
    def _vsg_rotate_quarter_turn(pdf, largo_mm, ancho_mm):
        """Gira la página un cuarto de vuelta y la deja del tamaño exacto.

        El cheque se compagina horizontal, que es como están medidas las
        coordenadas del diario, pero entra a la impresora por el lado corto.
        En lugar de rotar el HTML -wkhtmltopdf dibuja mal las transformaciones
        CSS- se marca la página con /Rotate: el visor y la impresora la
        presentan vertical.

        El tamaño de hoja de Odoo es un entero en milímetros, así que
        wkhtmltopdf compone sobre una página un poco más grande y aquí se
        ajusta a la medida real. El ajuste se ancla en la esquina superior
        izquierda, que es el origen de todas las coordenadas, de modo que no
        mueve ni un campo. Importa porque una página que no calza con el papel
        declarado hace que el dialogo de impresión la centre o la escale.
        """
        largo = largo_mm * 72.0 / 25.4
        ancho = ancho_mm * 72.0 / 25.4
        reader = PdfFileReader(io.BytesIO(pdf), strict=False)
        writer = PdfFileWriter()
        for page in reader.pages:
            caja = page.mediabox
            izquierda, arriba = float(caja.left), float(caja.top)
            # FloatObject hereda de decimal.Decimal: construido desde un float
            # escribe los 40 y tantos dígitos de la expansion binaria, y
            # Acrobat rechaza el archivo por exceder su limite de precision.
            # Pasandole el texto ya redondeado queda un número corto y exacto.
            medida = ArrayObject([
                generic.FloatObject("%.4f" % valor) for valor in (
                    izquierda, arriba - ancho, izquierda + largo, arriba)
            ])
            page[NameObject("/MediaBox")] = medida
            if "/CropBox" in page:
                page[NameObject("/CropBox")] = medida
            actual = int(page.get("/Rotate") or 0)
            page[NameObject("/Rotate")] = NumberObject((actual + 270) % 360)
            writer.add_page(page)
        buffer = io.BytesIO()
        writer.write(buffer)
        return buffer.getvalue()

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        content, content_type = super()._render_qweb_pdf(
            report_ref, res_ids=res_ids, data=data)
        if content_type != "pdf":
            return content, content_type
        report = self._get_report(report_ref)
        if report not in self._vsg_check_reports():
            return content, content_type
        journal = self._vsg_journal_of(report, res_ids)
        if self._vsg_sheet_is_vertical(journal):
            content = self._vsg_rotate_quarter_turn(
                content,
                journal.vsg_check_sheet_long or 190.5,
                journal.vsg_check_sheet_short or 98.42,
            )
        return content, content_type
