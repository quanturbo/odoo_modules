from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools.float_utils import float_is_zero

from .catalog import (
    CATEGORY,
    COMPONENTS,
    DEFAULT_DISCOUNT,
    DEMO_CUSTOMER,
    DEMO_REPLENISH_COMPONENT_KEY,
    DEMO_REPLENISH_QUANTITY,
    DEMO_SALE_QUANTITY,
    MODULE,
    PARENT_PRODUCT,
    VENDOR,
    VENDOR_DELAY_DAYS,
)


def post_init_hook(env):
    setup_shelving_kit(env)


def setup_shelving_kit(env):
    unit_uom = env.ref("uom.product_uom_unit")
    buy_route = env.ref("purchase_stock.route_warehouse0_buy")
    warehouse = env.ref("stock.warehouse0")
    stock_location = warehouse.lot_stock_id
    category = _setup_category(env)
    vendor = _setup_vendor(env)
    parent_product = _setup_parent_product(env, category, unit_uom)
    component_products = _setup_components(env, category, unit_uom, buy_route, vendor)
    bom = _setup_kit_bom(env, parent_product, component_products, unit_uom)

    for component in COMPONENTS:
        product = component_products[component["key"]]
        _setup_reorder_rule(env, component, product, unit_uom, buy_route, warehouse, stock_location)
        _set_stock_quantity(env, product, stock_location, component["stock_qty"])

    demo_records = _setup_demo_transactions(env, vendor, parent_product, component_products)
    _setup_navigation_domains(env, category, vendor, bom, demo_records)

    return bom


def _setup_vendor(env):
    values = {
        "name": VENDOR["name"],
        "is_company": True,
        "supplier_rank": 1,
        "email": VENDOR["email"],
    }
    return _upsert_record(env, VENDOR["xmlid"], "res.partner", values, [("name", "=", VENDOR["name"])])


def _setup_category(env):
    values = {
        "name": CATEGORY["name"],
        "parent_id": env.ref("product.product_category_goods").id,
    }
    return _upsert_record(env, CATEGORY["xmlid"], "product.category", values, [("name", "=", CATEGORY["name"])])


def _setup_demo_customer(env):
    values = {
        "name": DEMO_CUSTOMER["name"],
        "email": DEMO_CUSTOMER["email"],
        "customer_rank": 1,
    }
    return _upsert_record(env, DEMO_CUSTOMER["xmlid"], "res.partner", values, [("name", "=", DEMO_CUSTOMER["name"])])


def _setup_parent_product(env, category, unit_uom):
    values = {
        "name": PARENT_PRODUCT["name"],
        "default_code": PARENT_PRODUCT["sku"],
        "barcode": PARENT_PRODUCT["barcode"],
        "categ_id": category.id,
        "sale_ok": True,
        "purchase_ok": False,
        "is_storable": False,
        "list_price": PARENT_PRODUCT["sale_price"],
        "uom_id": unit_uom.id,
        "description_sale": PARENT_PRODUCT["description"],
    }
    return _upsert_record(
        env,
        PARENT_PRODUCT["xmlid"],
        "product.product",
        values,
        [("default_code", "=", PARENT_PRODUCT["sku"])],
    )


def _setup_components(env, category, unit_uom, buy_route, vendor):
    products = {}
    for component in COMPONENTS:
        product_xmlid = _product_xmlid(component)
        product_values = {
            "name": component["name"],
            "default_code": component["sku"],
            "categ_id": category.id,
            "sale_ok": False,
            "purchase_ok": True,
            "is_storable": True,
            "standard_price": _net_vendor_cost(component),
            "list_price": 0.0,
            "uom_id": unit_uom.id,
            "route_ids": [Command.link(buy_route.id)],
            "description_purchase": component["description"],
        }
        product = _upsert_record(
            env,
            product_xmlid,
            "product.product",
            product_values,
            [("default_code", "=", component["sku"])],
        )
        products[component["key"]] = product
        _setup_supplierinfo(env, component, product, vendor)
    return products


def _setup_supplierinfo(env, component, product, vendor):
    values = {
        "partner_id": vendor.id,
        "product_id": product.id,
        "product_code": component["vendor_code"],
        "product_name": component["name"],
        "price": component["vendor_list_price"],
        "discount": DEFAULT_DISCOUNT,
        "delay": component.get("vendor_delay_days", VENDOR_DELAY_DAYS),
    }
    return _upsert_record(
        env,
        _seller_xmlid(component),
        "product.supplierinfo",
        values,
        [("partner_id", "=", vendor.id), ("product_id", "=", product.id)],
    )


def _setup_kit_bom(env, parent_product, component_products, unit_uom):
    bom_values = {
        "code": "FG/RHG/DHG Kit",
        "product_tmpl_id": parent_product.product_tmpl_id.id,
        "product_qty": 1.0,
        "product_uom_id": unit_uom.id,
        "type": "phantom",
    }
    bom = _upsert_record(
        env,
        "bom_shelving_unit_48_18_84",
        "mrp.bom",
        bom_values,
        [("product_tmpl_id", "=", parent_product.product_tmpl_id.id), ("type", "=", "phantom")],
    )

    for component in COMPONENTS:
        product = component_products[component["key"]]
        line_values = {
            "bom_id": bom.id,
            "product_id": product.id,
            "product_qty": component["bom_qty"],
            "product_uom_id": unit_uom.id,
        }
        _upsert_record(
            env,
            _bom_line_xmlid(component),
            "mrp.bom.line",
            line_values,
            [("bom_id", "=", bom.id), ("product_id", "=", product.id)],
        )
    return bom


def _setup_reorder_rule(env, component, product, unit_uom, buy_route, warehouse, stock_location):
    if "reorder_min" not in component:
        return env["stock.warehouse.orderpoint"]

    values = {
        "name": f"Reorder {component['sku']}",
        "product_max_qty": component["reorder_max"],
        "product_min_qty": component["reorder_min"],
        "product_uom": unit_uom.id,
        "company_id": env.company.id,
        "warehouse_id": warehouse.id,
        "location_id": stock_location.id,
        "route_id": buy_route.id,
        "product_id": product.id,
    }
    return _upsert_record(
        env,
        _orderpoint_xmlid(component),
        "stock.warehouse.orderpoint",
        values,
        [("warehouse_id", "=", warehouse.id), ("location_id", "=", stock_location.id), ("product_id", "=", product.id)],
    )


def _set_stock_quantity(env, product, stock_location, target_quantity):
    quant_model = env["stock.quant"]
    current_quantity = quant_model._get_available_quantity(product, stock_location)
    delta = target_quantity - current_quantity
    if not float_is_zero(delta, precision_rounding=product.uom_id.rounding):
        quant_model._update_available_quantity(product, stock_location, delta)


def _setup_demo_transactions(env, vendor, parent_product, component_products):
    customer = _setup_demo_customer(env)
    sale_order = _setup_demo_sale_order(env, customer, parent_product, component_products)
    purchase_order = _setup_demo_purchase_order(env, vendor, component_products[DEMO_REPLENISH_COMPONENT_KEY])
    return {
        "sale_order": sale_order,
        "delivery": sale_order.picking_ids[:1],
        "purchase_order": purchase_order,
        "receipt": purchase_order.picking_ids[:1],
    }


def _setup_demo_sale_order(env, customer, parent_product, component_products):
    sale_order = env.ref(_full_xmlid("demo_sale_order_shelving_unit"), raise_if_not_found=False)
    if sale_order and _demo_sale_order_matches_components(sale_order, component_products):
        return sale_order

    sale_order = env["sale.order"].create({
        "partner_id": customer.id,
        "client_order_ref": "Shelving Kit Demo SO",
        "order_line": [Command.create({
            "product_id": parent_product.id,
            "product_uom_qty": DEMO_SALE_QUANTITY,
        })],
    })
    sale_order.action_confirm()
    sale_order.picking_ids.action_assign()
    _set_xmlid(env, "demo_sale_order_shelving_unit", sale_order)
    if sale_order.picking_ids:
        _set_xmlid(env, "demo_delivery_shelving_unit", sale_order.picking_ids[:1])
    return sale_order


def _demo_sale_order_matches_components(sale_order, component_products):
    if sale_order.state != "sale" or not sale_order.picking_ids:
        return False
    expected_quantities = {
        component_products[component["key"]].id: component["bom_qty"] * DEMO_SALE_QUANTITY
        for component in COMPONENTS
    }
    delivery_moves = sale_order.picking_ids.move_ids.filtered(lambda move: move.product_id.id in expected_quantities)
    actual_quantities = {
        move.product_id.id: move.product_uom_qty
        for move in delivery_moves
    }
    return actual_quantities == expected_quantities


def _setup_demo_purchase_order(env, vendor, component):
    purchase_order = env.ref(_full_xmlid("demo_purchase_order_upright_post_84"), raise_if_not_found=False)
    if purchase_order:
        return purchase_order

    orderpoint = env.ref(_full_xmlid(f"orderpoint_component_{DEMO_REPLENISH_COMPONENT_KEY}"))
    existing_line_ids = env["purchase.order.line"].search([
        ("orderpoint_id", "=", orderpoint.id),
        ("product_id", "=", component.id),
    ]).ids
    orderpoint.qty_to_order = DEMO_REPLENISH_QUANTITY
    orderpoint.action_replenish()
    purchase_order_line = env["purchase.order.line"].search([
        ("id", "not in", existing_line_ids),
        ("orderpoint_id", "=", orderpoint.id),
        ("product_id", "=", component.id),
        ("order_id.partner_id", "=", vendor.id),
    ], order="id desc", limit=1)
    if not purchase_order_line:
        raise UserError(f"Could not generate demo purchase order for {component.default_code}.")

    purchase_order = purchase_order_line.order_id
    purchase_order.origin = "Shelving Kit Demo Replenishment"
    purchase_order.button_confirm()
    purchase_order.picking_ids.action_assign()
    _set_xmlid(env, "demo_purchase_order_upright_post_84", purchase_order)
    _set_xmlid(env, "demo_purchase_order_line_upright_post_84", purchase_order_line)
    if purchase_order.picking_ids:
        _set_xmlid(env, "demo_receipt_upright_post_84", purchase_order.picking_ids[:1])
    return purchase_order


def _setup_navigation_domains(env, category, vendor, bom, demo_records):
    action_domains = {
        "action_shelving_demo_products": [("categ_id", "=", category.id)],
        "action_shelving_demo_bom": [("id", "=", bom.id)],
        "action_shelving_demo_bom_lines": [("bom_id", "=", bom.id)],
        "action_shelving_demo_vendor_prices": [("partner_id", "=", vendor.id)],
        "action_shelving_demo_reordering_rules": [("product_id.categ_id", "=", category.id)],
        "action_shelving_demo_sale_orders": [("id", "=", demo_records["sale_order"].id)],
        "action_shelving_demo_purchase_orders": [("id", "=", demo_records["purchase_order"].id)],
        "action_shelving_demo_receipts": [("id", "=", demo_records["receipt"].id)],
        "action_shelving_demo_receipt_lines": [("picking_id", "=", demo_records["receipt"].id)],
        "action_shelving_demo_deliveries": [("id", "=", demo_records["delivery"].id)],
        "action_shelving_demo_delivery_lines": [("picking_id", "=", demo_records["delivery"].id)],
    }
    for action_xmlid, domain in action_domains.items():
        action = env.ref(_full_xmlid(action_xmlid), raise_if_not_found=False)
        if action:
            action.domain = repr(domain)


def _upsert_record(env, xmlid_name, model_name, values, fallback_domain):
    record = env.ref(_full_xmlid(xmlid_name), raise_if_not_found=False)
    if not record and fallback_domain:
        record = env[model_name].search(fallback_domain, limit=1)
    if record:
        record.write(values)
    else:
        record = env[model_name].create(values)
    _set_xmlid(env, xmlid_name, record)
    return record


def _set_xmlid(env, xmlid_name, record):
    env["ir.model.data"]._update_xmlids([{
        "xml_id": _full_xmlid(xmlid_name),
        "record": record,
        "noupdate": True,
    }], update=True)


def _full_xmlid(xmlid_name):
    return f"{MODULE}.{xmlid_name}"


def _product_xmlid(component):
    return f"product_component_{component['key']}"


def _seller_xmlid(component):
    return f"seller_component_{component['key']}"


def _bom_line_xmlid(component):
    return f"bom_line_component_{component['key']}"


def _orderpoint_xmlid(component):
    return f"orderpoint_component_{component['key']}"


def _net_vendor_cost(component):
    return round(component["vendor_list_price"] * (1.0 - DEFAULT_DISCOUNT / 100.0), 2)