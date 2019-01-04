# -*- coding: utf-8 -*-
{
    'name': "Bridge Warehouse",

    'summary': """
        Crea un puente para mandar la mercancía del proveedor al cliente.
        """,

    'author': "César Gutierrez",
    'website': "http://www.yecora.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail', 'purchase','sale'],

    # always loaded
    'data': [
        'security/access_rules.xml',
        'security/ir.model.access.csv',
        'views/bridge_warehouse.xml',
        'views/buttons_order.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}