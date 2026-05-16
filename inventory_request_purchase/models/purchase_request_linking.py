# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import Command


REQUEST_CONTEXT_KEY = "stock_request_id"
PURCHASE_LINE_REQUEST_FIELD = "stock_request_ids"


PURCHASE_ACTION_XMLID = "purchase.purchase_rfq"
PURCHASE_FORM_VIEW_XMLID = "purchase.purchase_order_form"
PURCHASE_LIST_VIEW_XMLID = "purchase.purchase_order_tree"
REQUEST_ACTION_XMLID = "inventory_request_purchase.action_stock_request_form"
REQUEST_FORM_VIEW_XMLID = "inventory_request_purchase.view_stock_request_form"


def purchase_action_view_stack(env, multiple=False):
    form_view = env.ref(PURCHASE_FORM_VIEW_XMLID)
    if not multiple:
        return [(form_view.id, "form")]
    return [
        (env.ref(PURCHASE_LIST_VIEW_XMLID).id, "list"),
        (form_view.id, "form"),
    ]


def open_linked_purchase_orders(record, purchases):
    action = record.env["ir.actions.act_window"]._for_xml_id(PURCHASE_ACTION_XMLID)
    if len(purchases) > 1:
        action["domain"] = [("id", "in", purchases.ids)]
        action["views"] = purchase_action_view_stack(record.env, multiple=True)
    elif purchases:
        action["views"] = purchase_action_view_stack(record.env)
        action["res_id"] = purchases.id
    return action


def attach_request_to_purchase_values(line_values, procurement_values):
    request_id = procurement_values.get(REQUEST_CONTEXT_KEY)
    if request_id:
        line_values[PURCHASE_LINE_REQUEST_FIELD] = [
            *(line_values.get(PURCHASE_LINE_REQUEST_FIELD) or []),
            Command.link(request_id),
        ]
    return line_values


def open_inventory_requests(record, requests):
    action = record.env["ir.actions.act_window"]._for_xml_id(REQUEST_ACTION_XMLID)
    if len(requests) > 1:
        action["domain"] = [("id", "in", requests.ids)]
    elif requests:
        action["views"] = [(record.env.ref(REQUEST_FORM_VIEW_XMLID).id, "form")]
        action["res_id"] = requests.id
    return action
