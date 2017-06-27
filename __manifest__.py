# -*- coding: utf-8 -*-
{
    'name': "Vertical Publisher",

    'summary': """
    """,

    'description': """
        Vertical Publisher Management
        
        Manages a publisher system
        
        This module has been developed by Valentin Thirion, Jason PINDAT @ AbAKUS it-solutions.
    """,

    'author': "Valentin THIRION, Jason PINDAT, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",

    'category': 'Sale',
    'version': '10.0.1.0',

    'depends': [
        'base',
        'sale',
        'sale_workflow_rights'
    ],

    'data': [
        'views/production_type.xml',
        'views/production.xml',
        'views/sale_order.xml',
        'views/product_template.xml',
        'views/menu_buttons.xml'
    ],
}