{
    "name": "Valsegur Check Printing",
    "summary": "Impresión de cheques propios sobre formulario preimpreso, calibrable por banco",
    "version": "19.0.2.8.0",
    # Sin esto Odoo toma README.md como descripcion y lo pasa por docutils,
    # que no entiende las tablas de Markdown y escupe errores al actualizar.
    "description": "Impresion de cheques propios sobre el formulario preimpreso "
                   "del banco, calibrable por diario. Ver README.md.",
    "category": "Accounting/Accounting",
    "author": "ECM",
    "license": "LGPL-3",
    "depends": ["l10n_latam_check"],
    "external_dependencies": {"python": ["num2words"]},
    "data": [
        "security/ir.model.access.csv",
        "report/paperformat.xml",
        "report/report_actions.xml",
        "report/report_check.xml",
        "report/report_calibration.xml",
        "wizard/check_print_wizard_views.xml",
        "views/account_journal_views.xml",
        "views/l10n_latam_check_views.xml",
        "views/account_payment_views.xml",
    ],
    "installable": True,
    "application": False,
}
