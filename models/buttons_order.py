from openerp import fields, models, api
from decimal import Decimal

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    bridge_purchase_count = fields.Char(compute="_bridge_purchase_count")

    @api.multi
    def bridge_reception_tree(self):
        tree_res = self.env['ir.model.data'].get_object_reference('bridge_warehouse', 'bridge_warehouse_list')
        tree_id = tree_res and tree_res[1] or False
        form_res = self.env['ir.model.data'].get_object_reference('bridge_warehouse', 'bridge_warehouse_form_view')
        form_id = form_res and form_res[1] or False

        return{
            'type'          :   'ir.actions.act_window',
            'view_type'     :   'form', #Tampilan pada tabel pop-up
            'view_mode'     :   'tree,form', # Menampilkan bagian yang di pop up, tree = menampilkan tabel tree nya utk product
            'res_model'     :   'bridge.warehouse', #Menampilkan tabel yang akan di show di pop-up screen
            'target'        :   'new', # Untuk menjadikan tampilan prduct yang dipilih menjadi pop-up table tampilan baru, jika dikosongin maka tidak muncul pop-up namun muncul halaman baru.
            'views'         :   [(tree_id, 'tree'),(form_id, 'form')],
            'domain'        :   [('purchase_order.id','=', self.id)] #Filter id barang yang ditampilkan
            }

    @api.multi
    def _bridge_purchase_count(self):
        tons = 0
        for itr in self.env['bridge.warehouse'].search([('purchase_order.id','=', self.id)]):
            tons += itr['clean_kilos']
        tons = tons / 1000
        self.bridge_purchase_count = str(round(tons,2)) + 'tn'


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bridge_sale_count = fields.Char(compute="_bridge_sale_count")

    @api.multi
    def bridge_reception_tree(self):
        tree_res = self.env['ir.model.data'].get_object_reference('bridge_warehouse', 'bridge_warehouse_list')
        tree_id = tree_res and tree_res[1] or False
        form_res = self.env['ir.model.data'].get_object_reference('bridge_warehouse', 'bridge_warehouse_form_view')
        form_id = form_res and form_res[1] or False

        return{
            'type'          :   'ir.actions.act_window',
            'view_type'     :   'form', #Tampilan pada tabel pop-up
            'view_mode'     :   'tree,form', # Menampilkan bagian yang di pop up, tree = menampilkan tabel tree nya utk product
            'res_model'     :   'bridge.warehouse', #Menampilkan tabel yang akan di show di pop-up screen
            'target'        :   'new', # Untuk menjadikan tampilan prduct yang dipilih menjadi pop-up table tampilan baru, jika dikosongin maka tidak muncul pop-up namun muncul halaman baru.
            'views'         :   [(tree_id, 'tree'),(form_id, 'form')],
            'domain'        :   [('sale_order.id','=', self.id)] #Filter id barang yang ditampilkan
            }


    @api.multi
    def _bridge_sale_count(self):
        tons = 0
        for itr in self.env['bridge.warehouse'].search([('sale_order.id','=', self.id)]):
            tons += itr['clean_kilos']
        tons = tons / 1000
        self.bridge_sale_count = str(round(tons,2)) + 'tn'