{
    "name": "Valsegur Legacy Fields",
    "summary": "Audit fields for historical accounting migrations",
    "version": "19.0.2.0.0",
    "category": "Accounting/Accounting",
    "author": "ECM",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_legacy_import_batch_views.xml",
    ],
    "installable": True,
    "application": False,
}
