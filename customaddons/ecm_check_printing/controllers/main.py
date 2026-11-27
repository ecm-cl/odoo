from urllib.parse import urlencode

from markupsafe import Markup, escape

from odoo import _, http
from odoo.exceptions import UserError
from odoo.http import request

REPORT = "ecm_check_printing.report_vsg_check"

# Página minima que carga el PDF y pide el dialogo de impresión del sistema.
# El visor de PDF de Chrome y de Edge acepta print() cuando el documento es del
# mismo origen, que es el caso. Si el navegador lo bloquea queda el boton.
PAGINA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<title>Imprimir cheque</title>
<style>
 html, body { margin:0; height:100%%; font-family:sans-serif; }
 iframe { border:0; width:100%%; height:calc(100%% - 42px); }
 .barra { height:42px; display:flex; align-items:center; gap:12px; padding:0 12px;
          background:#f4f4f5; border-bottom:1px solid #d8d8dc; box-sizing:border-box; }
 button { padding:4px 14px; cursor:pointer; }
</style>
</head>
<body>
<div class="barra">
  <button onclick="imprimir()">Imprimir</button>
  <span>Pon el cheque en la bandeja con el lado corto hacia el alimentador.</span>
</div>
<iframe id="cheque" src="%(url)s"></iframe>
<script>
function imprimir() {
    var marco = document.getElementById('cheque');
    try {
        marco.contentWindow.focus();
        marco.contentWindow.print();
    } catch (e) {
        window.open(marco.src, '_blank');
    }
}
document.getElementById('cheque').addEventListener('load', function () {
    // algunos visores necesitan un instante después del load para aceptar print()
    setTimeout(imprimir, 400);
});
</script>
</body>
</html>"""


class VsgCheckPrinting(http.Controller):

    def _vsg_checks(self, ids):
        """Cheques pedidos, validando que el usuario los pueda leer."""
        try:
            check_ids = [int(i) for i in (ids or "").split(",") if i.strip()]
        except ValueError:
            raise UserError(_("La lista de cheques no es válida."))
        if not check_ids:
            raise UserError(_("No se indico ningún cheque."))
        checks = request.env["l10n_latam.check"].browse(check_ids)
        checks.check_access("read")
        return checks.exists()

    @staticmethod
    def _vsg_params(ids, endorsement, crossed, year_prefix, sheet):
        return {
            "ids": ids or "",
            "endorsement": endorsement if endorsement in
            ("nominativo", "orden", "portador") else "nominativo",
            "crossed": "1" if crossed == "1" else "0",
            "year_prefix": "1" if year_prefix == "1" else "0",
            "sheet": "carta" if sheet == "carta" else "cheque",
        }

    @http.route("/vsg_check_printing/pdf", type="http", auth="user")
    def vsg_check_pdf(self, ids="", endorsement="nominativo", crossed="0",
                      year_prefix="1", sheet="cheque", **kw):
        """El PDF del cheque, servido en línea para que el visor lo imprima."""
        params = self._vsg_params(ids, endorsement, crossed, year_prefix, sheet)
        checks = self._vsg_checks(params["ids"])
        reports = request.env["ir.actions.report"].with_context(
            vsg_check_letter=params["sheet"] == "carta")
        pdf, _dummy = reports._render_qweb_pdf(
            REPORT,
            checks.ids,
            data={
                "vsg_endorsement": params["endorsement"],
                "vsg_crossed": params["crossed"] == "1",
                "vsg_year_prefix": params["year_prefix"] == "1",
            },
        )
        return request.make_response(pdf, headers=[
            ("Content-Type", "application/pdf"),
            ("Content-Length", len(pdf)),
            ("Content-Disposition", 'inline; filename="cheque.pdf"'),
        ])

    @http.route("/vsg_check_printing/print", type="http", auth="user")
    def vsg_check_print(self, ids="", endorsement="nominativo", crossed="0",
                        year_prefix="1", sheet="cheque", **kw):
        """Página que carga el cheque y abre el dialogo de impresión."""
        params = self._vsg_params(ids, endorsement, crossed, year_prefix, sheet)
        self._vsg_checks(params["ids"])
        url = "/vsg_check_printing/pdf?%s" % urlencode(params)
        return request.make_response(
            Markup(PAGINA) % {"url": escape(url)},
            headers=[("Content-Type", "text/html; charset=utf-8")],
        )
