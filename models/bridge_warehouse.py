# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from openerp.exceptions import ValidationError
import datetime
import pytz

class Bridgewarehouse(models.Model):
    _name = 'bridge.warehouse'
    _inherit = ['mail.thread']

    # name = fields.Char('Bridge Warehouse', required=True, select=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('brige.warehouse.code'), help="Unique number of bridge warehouse")
    name = fields.Char()
    purchase_order = fields.Many2one('purchase.order', 'Contrato de compra')
    sale_order = fields.Many2one('sale.order', 'Contrato de venta')

    location_purchase_id = fields.Many2one('stock.location', 'Ubicación de entrada')
    location_sale_id = fields.Many2one('stock.location', 'Ubicación de salida')

    
    owner_id = fields.Many2one('res.partner', 'Propietario')
    product_id = fields.Many2one('product.product', 'Producto', compute="_compute_product_id", store=False, readonly=True)
    datetime = fields.Datetime('Fecha')
    driver = fields.Char('Conductor')
    car_plates = fields.Char('Placas')

    humidity_rate = fields.Float('Humedad')
    density = fields.Float('Densidad')
    temperature = fields.Float('Temperatura')
    damage_rate = fields.Float('Daño')
    break_rate = fields.Float('Quebrado')
    impurity_rate = fields.Float('Impureza')
    
    humid_kilos = fields.Float('kilos húmedos', compute="_compute_humid_kilos", store=False)
    damaged_kilos = fields.Float('Kilos dañado', compute="_compute_damaged_kilos", store=False)
    broken_kilos = fields.Float('Kilos quebrados', compute="_compute_broken_kilos", store=False)
    impure_kilos = fields.Float('Kilos Impuros', compute="_compute_impure_kilos", store=False)

    deducted_kilos = fields.Float('Kilos Deducidos', compute="_compute_deducted_kilos", store=False)

    input_kilos = fields.Float('Kilos de entrada')
    output_kilos = fields.Float('Kilos de salida')
    raw_kilos = fields.Float('Kilos netos', compute="_compute_raw_kilos", store=False)
    clean_kilos = fields.Float('Kilos Limpios origen', compute="_compute_clean_kilos", store=False)

    stock_picking_purchase_id = fields.Many2one('stock.picking', 'Movimiento de entrada de almacen', readonly=True)
    stock_picking_sale_id = fields.Many2one('stock.picking', 'Movimiento de salida de almacen', readonly=True)
   
    state = fields.Selection([
        ('analysis', 'Analisis'),
        ('weight_input', 'Peso de Entrada'),
        ('weight_output', 'Pesos de Salida'),
        ('done', 'Hecho'),
    ], default='analysis')

    #Functions
    @api.multi
    def _compute_product_id(self):
        product_id = False
        for line in self.purchase_order.order_line:
            product_id = line.product_id
            break
        self.product_id = product_id

    @api.onchange('purchase_order')
    def _onchange_date(self):
        local = pytz.timezone("America/Chihuahua")
        utc = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
        local_hr = local.localize(utc, is_dst=None)
        self.datetime = local_hr

    @api.one
    @api.depends('raw_kilos', 'humidity_rate')
    def _compute_humid_kilos(self):
        if self.humidity_rate > 14:
            self.humid_kilos = self.raw_kilos * (self.humidity_rate - 14) * .0116
        else:
            self.humid_kilos = 0

    @api.one
    def _compute_damaged_kilos(self):
        if self.damage_rate > 5:
            self.damaged_kilos = self.raw_kilos * (self.damage_rate - 5) / 100
        else:
            self.damaged_kilos = 0

    @api.one
    def _compute_broken_kilos(self):
        if self.break_rate > 2:
            self.broken_kilos = self.raw_kilos * (self.break_rate - 2) / 100
        else:
            self.broken_kilos = 0

    @api.one
    @api.depends('impurity_rate')
    def _compute_impure_kilos(self):
        if self.impurity_rate > 2:
            self.impure_kilos = self.raw_kilos * (self.impurity_rate - 2) / 100
        else:
            self.impure_kilos = 0

    @api.one
    @api.depends('input_kilos', 'output_kilos')
    def _compute_raw_kilos(self):
        self.raw_kilos = self.input_kilos - self.output_kilos

    @api.one
    @api.depends('raw_kilos','deducted_kilos')
    def _compute_clean_kilos(self):
        self.clean_kilos = self.raw_kilos - self.deducted_kilos

    @api.one
    @api.depends('humid_kilos','damaged_kilos','broken_kilos')
    def _compute_deducted_kilos(self):
        self.deducted_kilos = self.humid_kilos + self.damaged_kilos + self.broken_kilos + self.impure_kilos

    @api.multi
    def write(self, vals, recursive=None):
        if not recursive:
            if self.state == 'analysis':
                self.write({'state': 'weight_input'}, 'r')
            elif self.state == 'weight_input':
                self.write({'state': 'weight_output'}, 'r')
            elif self.state == 'weight_output':
                self.write({'state': 'done'}, 'r')

        res = super(Bridgewarehouse, self).write(vals)
        return res
    
    @api.model
    def create(self, vals):
        vals['state'] = 'weight_input'
        vals['name'] = self.env['ir.sequence'].next_by_code('brige.warehouse.code')
        res = super(Bridgewarehouse, self).create(vals)
        return res
    
    @api.one
    def transfer(self):
        self.stock_picking_purchase_id = self.env['stock.picking'].search([('origin', '=', self.purchase_order.name), ('state', '=', 'assigned')], order='date', limit=1)
        self.stock_picking_sale_id = self.env['stock.picking'].search([('origin', '=', self.sale_order.name), ('state', '=', 'assigned')], order='date', limit=1)
        if self.stock_picking_purchase_id and self.stock_picking_sale_id:
            picking = [self.stock_picking_purchase_id.id]
            picking_sale = [self.stock_picking_sale_id.id]
            for move in self.stock_picking_purchase_id.move_lines:
                move.location_dest_id = self.location_purchase_id
                self._do_enter_transfer_details(picking, self.stock_picking_purchase_id, self.clean_kilos, 'purchase')
            for move in self.stock_picking_sale_id.move_lines:
                move.location_id = self.location_sale_id
                self._do_enter_transfer_details(picking_sale, self.stock_picking_sale_id, self.clean_kilos, 'sale')
        else:   
             raise exceptions.ValidationError("No se puede crear el movimiento de almacén, favor de revisar los pedidos")
    
    @api.multi
    def _do_enter_transfer_details(self, picking_id, picking, clean_kilos, type):
        context = dict(self._context or {})
        context.update({
            'active_model': self._name,
            'active_ids': picking_id,
            'active_id': len(picking_id) and picking_id[0] or False
        })
        created_id = self.env['stock.backorder.confirmation'].with_context(context).create({'picking_id': len(picking_id) and picking_id[0] or False})
        if self.owner_id.id:
            picking.write({'owner_id': self.owner_id.id})
            picking.action_assign_owner()
        if not picking.pack_operation_product_ids:
            picking.do_prepare_partial()
        if type == 'purchase':
            for op in picking.pack_operation_product_ids:
                op.write({'qty_done':clean_kilos/1000, "location_dest_id": self.location_purchase_id.id})
        if type == 'sale':
            for op in picking.pack_operation_product_ids:
                op.write({'qty_done':clean_kilos/1000, "location_id": self.location_sale_id.id})
        created_id.process()


