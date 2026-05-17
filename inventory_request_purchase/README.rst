Inventory Request Purchasing
============================

Inventory Request Purchasing gives warehouse and purchasing teams one clear workflow for internal stock requests, urgent priorities, and purchase follow-up.

It helps users see what is still waiting, what has already been ordered or received, and which purchase documents cover each request. The workflow is kept in one Odoo application with clear model and view separation, so it stays easier to use day to day and easier to extend later.

This is a single Odoo 19 addon for internal inventory requests and purchase procurement tracking.

Scope
=====

This addon replaces the previous split workflow with one installable application. It depends directly on Odoo Inventory and Purchase modules and is intended for Odoo 19.

Features
========

* Inventory request and request order menus under Inventory.
* Requests for product, quantity, warehouse, destination location, and expected date.
* Request orders for grouping several request lines under one replenishment need.
* Priority, expected-date, overdue, and high-priority tracking for daily follow-up.
* Internal notes for requester context, receiving instructions, and purchase constraints.
* Purchase order line links back to inventory requests.
* Smart buttons from requests to purchases, and from purchases to requests.
* Allocation tracking from stock moves and receipts back to the original request.
* Company-aware request, allocation, and request-order access rules.
* Settings for request orders, virtual locations, and available-stock-first behavior.

Assumptions
===========

* Odoo 19 is used.
* Inventory, Purchase, and Purchase Stock are installed through this addon's dependencies.
* Existing technical model names are kept where needed for Odoo continuity, while user-facing menus and labels use Inventory Request wording.
* This is one application workflow; the old split addon folders are not required.

Structure Notes
===============

The addon keeps separate Python files for separate Odoo model extensions. This is normal Odoo practice and makes it clear which behavior belongs to requests, purchase orders, stock moves, receipts, settings, and company-safety constraints.

The view files follow the same rule: request screens, request order screens, allocation screens, purchase links, receipt links, settings, and menus are separate because they inherit or define different Odoo UI records.

The previous optional product-context server action was removed because users can create requests from the Inventory Request workflow directly and the extra action was outside the agreed scope.

Validation
==========

The module was validated with an update and focused smoke tests on ``odoo_test_shelving_final6``.

Run the same validation with::

    D:\user\programs\odoo_\python\python.exe .\odoo-bin -c .\odoo.conf -d odoo_test_shelving_final6 -u inventory_request_purchase --test-enable --test-tags inventory_request_purchase --stop-after-init --no-http

Expected result::

    0 failed, 0 error(s)
