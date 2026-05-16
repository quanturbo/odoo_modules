MODULE = "shelving_kit_demo"
DEFAULT_DISCOUNT = 65.0
VENDOR_DELAY_DAYS = 14
DEMO_SALE_QUANTITY = 1.0
DEMO_REPLENISH_COMPONENT_KEY = "upright_post_84"
DEMO_REPLENISH_QUANTITY = 1.0

VENDOR = {
    "xmlid": "vendor_rapid_home_goods",
    "name": "Rapid Home Goods Manufacturing",
    "email": "purchasing@example.invalid",
}

CATEGORY = {
    "xmlid": "category_free_standing_shelving",
    "name": "Free-Standing Shelving",
}

DEMO_CUSTOMER = {
    "xmlid": "customer_shelving_demo",
    "name": "Shelving Kit Demo Customer",
    "email": "demo.customer@example.invalid",
}

PARENT_PRODUCT = {
    "xmlid": "product_shelving_unit_48_18_84",
    "sku": "FG/RHG/DHG",
    "name": "4-foot Double-Sided Free-Standing Shelving Unit",
    "description": "48-18-84-FST-PERFOREE-CLOSE-10-10-10",
    "sale_price": 1495.00,
    "barcode": "FG-RHG-DHG-48-18-84",
}

COMPONENTS = (
    {
        "key": "upright_post_84",
        "sku": "RHG-POST-84",
        "name": "84-inch Upright Post",
        "description": "Manufacturer upright post for 84-inch shelving height.",
        "vendor_code": "MFG-POST84",
        "vendor_list_price": 120.00,
        "bom_qty": 4.0,
        "stock_qty": 16.0,
        "reorder_min": 8.0,
        "reorder_max": 24.0,
    },
    {
        "key": "base_foot_left_18",
        "sku": "RHG-BASE-FOOT-18-L",
        "name": "18-inch Left Base Foot",
        "description": "Left base foot for free-standing shelving.",
        "vendor_code": "MFG-BF18L",
        "vendor_list_price": 55.00,
        "bom_qty": 2.0,
        "stock_qty": 8.0,
    },
    {
        "key": "base_foot_right_18",
        "sku": "RHG-BASE-FOOT-18-R",
        "name": "18-inch Right Base Foot",
        "description": "Right base foot for free-standing shelving.",
        "vendor_code": "MFG-BF18R",
        "vendor_list_price": 55.00,
        "bom_qty": 2.0,
        "stock_qty": 8.0,
    },
    {
        "key": "front_crossbar_48",
        "sku": "DHG-CROSSBAR-48-F",
        "name": "48-inch Front Cross-Bar",
        "description": "Front horizontal cross-bar for 48-inch bay.",
        "vendor_code": "MFG-XB48F",
        "vendor_list_price": 90.00,
        "bom_qty": 2.0,
        "stock_qty": 8.0,
    },
    {
        "key": "rear_crossbar_48",
        "sku": "DHG-CROSSBAR-48-R",
        "name": "48-inch Rear Cross-Bar",
        "description": "Rear horizontal cross-bar for 48-inch bay.",
        "vendor_code": "MFG-XB48R",
        "vendor_list_price": 90.00,
        "bom_qty": 2.0,
        "stock_qty": 8.0,
    },
    {
        "key": "perforated_back_panel_48_84",
        "sku": "DHG-BACK-PERF-48X84",
        "name": "48 x 84 Perforated Backing Panel",
        "description": "Perforated backing panel for one side of the unit.",
        "vendor_code": "MFG-PERF4884",
        "vendor_list_price": 320.00,
        "bom_qty": 1.0,
        "stock_qty": 4.0,
        "reorder_min": 2.0,
        "reorder_max": 8.0,
        "vendor_delay_days": 21,
    },
    {
        "key": "closed_back_panel_48_84",
        "sku": "DHG-BACK-CLOSE-48X84",
        "name": "48 x 84 Closed Backing Panel",
        "description": "Closed backing panel for one side of the unit.",
        "vendor_code": "MFG-CLOSE4884",
        "vendor_list_price": 300.00,
        "bom_qty": 1.0,
        "stock_qty": 4.0,
        "vendor_delay_days": 21,
    },
    {
        "key": "front_kick_plate_48",
        "sku": "DHG-KICK-48-F",
        "name": "48-inch Front Kick Plate",
        "description": "Front kick plate for base protection.",
        "vendor_code": "MFG-KP48F",
        "vendor_list_price": 70.00,
        "bom_qty": 1.0,
        "stock_qty": 5.0,
    },
    {
        "key": "rear_kick_plate_48",
        "sku": "DHG-KICK-48-R",
        "name": "48-inch Rear Kick Plate",
        "description": "Rear kick plate for base protection.",
        "vendor_code": "MFG-KP48R",
        "vendor_list_price": 70.00,
        "bom_qty": 1.0,
        "stock_qty": 5.0,
    },
    {
        "key": "upright_top_cap",
        "sku": "RHG-TOP-CAP",
        "name": "Upright Post Top Cap",
        "description": "Plastic cap for the top of each upright post.",
        "vendor_code": "MFG-TOPCAP",
        "vendor_list_price": 10.00,
        "bom_qty": 4.0,
        "stock_qty": 20.0,
    },
    {
        "key": "hardware_pack",
        "sku": "RHG-HARDWARE-KIT",
        "name": "Shelving Hardware Pack",
        "description": "Bolt, washer, and connector hardware pack for one kit.",
        "vendor_code": "MFG-HWPK",
        "vendor_list_price": 40.00,
        "bom_qty": 1.0,
        "stock_qty": 10.0,
        "reorder_min": 5.0,
        "reorder_max": 15.0,
    },
    {
        "key": "leveler_pack",
        "sku": "RHG-LEVELER-KIT",
        "name": "Adjustable Leveler Pack",
        "description": "Adjustable feet and levelers for one free-standing kit.",
        "vendor_code": "MFG-LVLPK",
        "vendor_list_price": 25.00,
        "bom_qty": 1.0,
        "stock_qty": 10.0,
    },
)