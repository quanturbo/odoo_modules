# Shelving Kit Demo

This module helps a company sell a kit product without losing control of stock availability or supplier cost logic. When the parent kit is sold, Odoo reserves the real component items, which reduces overselling and fulfillment mistakes. It also stores vendor list price and discount separately, so net cost updates automatically when supplier prices change.

This addon builds a complete Odoo 19 inventory, purchasing, sales, and kit BoM setup for one sellable shelving SKU:

- Parent SKU: `FG/RHG/DHG`
- Description: `48-18-84-FST-PERFOREE-CLOSE-10-10-10`
- Product: 4-foot Double-Sided Free-Standing Shelving Unit

The parent product is sold as a kit. It is not manufactured and is not itself stocked. Odoo explodes the kit BoM into stock moves for the stocked components when the sale order is confirmed.

## What Is Included

- Vendor: Rapid Home Goods Manufacturing
- 12 stocked component SKUs covering posts, feet, cross-bars, backing panels, kick plates, caps, hardware, and levelers
- Vendor pricing on every component using Odoo's native supplier list price and discount fields
- A phantom/kit BoM for the parent SKU
- Reorder rules on posts, perforated backing panels, and hardware packs
- Initial on-hand stock for every component in the main warehouse
- Shelving Demo menus under Inventory and Manufacturing that open the seeded products, kit BoM, kit component lines, vendor prices, reordering rules, sale order, purchase order, receipt lines, and delivery lines
- Demo sale and purchase transactions created through normal Odoo workflows so the UI is not empty on a fresh test database
- Post-install tests for the sale-order kit reservation flow and purchase-order receipt flow

The catalog is maintained in named Python constants in `catalog.py`, not as a long hardcoded XML business-data file. To change a SKU, quantity, vendor list price, vendor code, reorder threshold, or initial stock quantity, update the matching entry in `COMPONENTS` and reinstall the addon on a disposable test database. XML is used only for Odoo UI metadata: menus and window actions.

## Vendor Pricing Design

Odoo 19 already supports the required pricing structure on `product.supplierinfo`:

- `price` stores the vendor list price
- `discount` stores the negotiated discount percentage
- `price_discounted` is computed from those two fields and is used by purchase orders

For example, the upright post has a vendor list price of 120.00 and a 65 percent discount. Odoo computes the net purchase price as 42.00. If the vendor list price later changes to 200.00, the same discount automatically makes the computed net price 70.00.

Component `standard_price` values are seeded to the initial net costs so test valuation starts from realistic placeholder costs. Future purchase costs should be managed from vendor pricelists, not by manually maintaining standard costs per component.

## Replicate Or Extend

1. Install the addon on a fresh Odoo 19 Enterprise or Community test database with Sales, Inventory, Purchase, and Manufacturing available.
2. Confirm the parent product `FG/RHG/DHG` has BoM `FG/RHG/DHG Kit` with BoM type `Kit`.
3. Add or update components by editing the `COMPONENTS` tuple in `catalog.py`.
4. Keep vendor list pricing in `vendor_list_price` and the negotiated discount in `DEFAULT_DISCOUNT`.
5. Keep BoM quantities in `bom_qty`; these become `mrp.bom.line` quantities under the kit BoM.
6. Add `reorder_min` and `reorder_max` only for components that need replenishment rules.

## UI Demo Flow

After installation, open Inventory > Shelving Demo:

1. Products shows the parent SKU and all stocked components.
2. Kit BoM shows the phantom BoM for `FG/RHG/DHG`.
3. Kit Components shows the exact component quantities on the kit BoM.
4. Vendor Prices shows list prices, the 65 percent discount, and computed net purchase prices.
5. Demo Sales Orders shows a confirmed sale order for one parent kit; Demo Delivery Lines shows the 12 reserved component moves.
6. Demo Purchase Orders shows a purchase order generated from the upright-post reordering rule.
7. Demo Receipts shows the incoming receipt header; Demo Receipt Lines shows the receivable upright-post move.

Manufacturing > Shelving Kit Demo opens the same kit BoM and kit component lines. Manufacturing Orders is intentionally empty because this setup uses a Kit BoM (`phantom`) and does not manufacture the parent product.

## Suggested Validation Commands

Use a disposable database because module installation and tests create business records:

```powershell
D:\user\programs\odoo_\python\python.exe .\odoo-bin -c .\odoo.conf -d odoo_test_shelving -i shelving_kit_demo --test-enable --test-tags shelving_kit_demo --stop-after-init --no-http
```

Manual checks:

1. Create a sale order for quantity 1 of `FG/RHG/DHG` and confirm it. The delivery should contain component moves, not a parent stock move.
2. Run replenishment for reorder-flagged component `RHG-POST-84`. Odoo should generate a purchase order to Rapid Home Goods Manufacturing; confirm it, receive it, and verify on-hand quantity increases.