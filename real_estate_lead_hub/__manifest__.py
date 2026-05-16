{
    "name": "Real Estate Lead Hub",
    "summary": "Import and qualify real estate leads for CRM",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "Custom Development",
    "category": "Sales/CRM",
    "depends": ["crm"],
    "data": [
        "security/real_estate_lead_security.xml",
        "security/ir.model.access.csv",
        "views/real_estate_lead_inbox_views.xml",
        "views/real_estate_lead_source_views.xml",
        "views/real_estate_lead_menu.xml",
    ],
    "installable": True,
    "application": False,
}