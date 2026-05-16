# Installation Guide

> Tested with Odoo 19.0 Community Edition.

## Prerequisites

| Requirement | Version |
|---|---|
| Odoo | 19.0 |
| Python | 3.10+ |
| PostgreSQL | 14+ |

## Step 1 – Copy modules

Place each module folder under your Odoo `addons_path`:

```
/opt/odoo/custom_addons/
├── shelving_kit_demo/
├── real_estate_lead_hub/
└── inventory_request_purchase/
```

Or add this repository path directly in `odoo.conf`:

```ini
[options]
addons_path = /opt/odoo/addons,/opt/odoo/custom_addons
```

## Step 2 – Install dependencies

No external Python packages required. All dependencies are standard Odoo modules:

- `shelving_kit_demo` → `sale_mrp`, `purchase_stock`
- `real_estate_lead_hub` → `crm`
- `inventory_request_purchasing` → `stock`, `purchase`, `purchase_stock`

## Step 3 – Install via CLI

```bash
./odoo-bin -c odoo.conf \
  -d your_database \
  -u shelving_kit_demo,real_estate_lead_hub,inventory_request_purchasing
```

Or install from the **Apps** menu in the Odoo backend (activate developer mode first).

## Step 4 – Verify

After install:

- **Shelving Kit Demo** → Inventory → Shelving Kit menu appears
- **Real Estate Lead Hub** → CRM → Lead Inbox appears
- **Inventory Request Purchasing** → Inventory → Stock Requests appears

## Updating

```bash
./odoo-bin -c odoo.conf -d your_database \
  -u shelving_kit_demo,real_estate_lead_hub,inventory_request_purchasing \
  --stop-after-init
```
