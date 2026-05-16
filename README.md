# Odoo Modules

Three custom Odoo 19 addons developed as a single delivery unit.

---

## Modules

### Shelving Kit Demo
**Category:** Inventory  
**Depends:** `sale_mrp`, `purchase_stock`

Sets up a 4-foot double-sided shelving unit as a kit Bill of Materials. Demonstrates how Odoo links manufacturing BoMs, vendor pricing, reordering rules, and sale/purchase order flows for a single physical product.

### Real Estate Lead Hub
**Category:** Sales / CRM  
**Depends:** `crm`

Provides a structured inbox for importing and qualifying real estate leads before they enter the CRM pipeline. Supports multiple lead sources, payload tracking, and configurable security roles for intake teams.

### Inventory Request Purchasing
**Category:** Inventory  
**Depends:** `stock`, `purchase`, `purchase_stock`

Bridges internal inventory requests with the purchasing workflow. Operators raise stock requests, which are allocated and traced through to confirmed purchase orders — keeping demand and supply linked in one view.

---

## Requirements

- Odoo 19.0 Community or Enterprise
- PostgreSQL 14+

Install each module via **Apps → Upload Module** or by placing the folder inside your configured `addons_path` and running:

```bash
./odoo-bin -u shelving_kit_demo,real_estate_lead_hub,inventory_request_purchasing -d <your_db>
```

---

## Repository structure

```
odoo_modules/
├── shelving_kit_demo/
├── real_estate_lead_hub/
└── inventory_request_purchase/
```

Each module lives at the repository root — no extra wrapper folder needed.

---

## Branching model

| Branch | Purpose |
|---|---|
| `main` | Stable, production-ready code |
| `dev` | Integration — all feature branches merge here first |
| `feature/*` | One focused change per branch |
| `docs/*` | Documentation-only changes |
| `workflow/*` | Workflow and tooling changes |

Typical flow:

1. Cut a branch from `dev`.
2. Commit focused changes.
3. Push and open a PR against `dev`.
4. After review, merge `dev` → `main` and tag a release.

---

## License

LGPL-3.0

