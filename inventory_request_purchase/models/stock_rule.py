# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models

from .purchase_request_linking import attach_request_to_purchase_values


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def run(self, procurements, raise_user_error=True):
        rewritten_procurements = []
        indexes_to_replace = []
        for index, procurement in enumerate(procurements):
            request_id = procurement.values.get("stock_request_id")
            if not request_id:
                continue
            request = self.env["stock.request"].browse(request_id)
            if request.order_id:
                rewritten_procurements.append(procurement._replace(origin=request.order_id.name))
                indexes_to_replace.append(index)
        for index in reversed(indexes_to_replace):
            procurements.pop(index)
        procurements.extend(rewritten_procurements)
        return super().run(procurements, raise_user_error=raise_user_error)

    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        result = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
        if values.get("stock_request_id", False):
            result["allocation_ids"] = [
                (
                    0,
                    0,
                    {
                        "stock_request_id": values.get("stock_request_id"),
                        "requested_product_uom_qty": product_qty,
                    },
                )
            ]
        return result

    def _update_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, line
    ):
        line_values = super()._update_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, line
        )
        return attach_request_to_purchase_values(line_values, values)

