{
    "name": "Shelving Kit Demo",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Inventory and kit BoM setup for a 4-foot double-sided shelving unit",
    "author": "Bencium",
    "depends": ["sale_mrp", "purchase_stock"],
    "data": [
        "views/shelving_kit_demo_menus.xml",
    ],
    "post_init_hook": "post_init_hook",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
}