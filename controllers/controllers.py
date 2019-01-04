# -*- coding: utf-8 -*-
from odoo import http

# class Odoo10Modules/bridgeWarehouse(http.Controller):
#     @http.route('/odoo_10_modules/bridge_warehouse/odoo_10_modules/bridge_warehouse/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_10_modules/bridge_warehouse/odoo_10_modules/bridge_warehouse/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_10_modules/bridge_warehouse.listing', {
#             'root': '/odoo_10_modules/bridge_warehouse/odoo_10_modules/bridge_warehouse',
#             'objects': http.request.env['odoo_10_modules/bridge_warehouse.odoo_10_modules/bridge_warehouse'].search([]),
#         })

#     @http.route('/odoo_10_modules/bridge_warehouse/odoo_10_modules/bridge_warehouse/objects/<model("odoo_10_modules/bridge_warehouse.odoo_10_modules/bridge_warehouse"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_10_modules/bridge_warehouse.object', {
#             'object': obj
#         })