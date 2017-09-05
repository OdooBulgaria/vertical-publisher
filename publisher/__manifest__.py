# -*- coding: utf-8 -*-
{
    'name': "Publisher",

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
        'project',
        'contacts',
        'partner_sector',
        'sale_workflow_rights',
        'sale_contract'
    ],

    'data': [
        'views/media.xml',
        'views/format.xml',
        'views/location.xml',
        'views/color.xml',
        'views/production_type.xml',
        'views/production_line.xml',
        'views/production.xml',
        'views/res_partner.xml',
        'views/product_template.xml',
        'views/sale_order.xml',
        'views/project_project.xml',
        'views/invitation.xml',
        'views/project_template.xml',
        'views/account_invoice.xml',
        'views/sale_subscription.xml',
        'views/account_fiscal_position.xml',

        'views/menu_buttons.xml',

        'views/company_config.xml',

        'report/layout.xml',
        'report/sale_report_templates.xml',
        'report/sale_report.xml',
        'report/production_report_templates.xml',
        'report/production_report.xml',
        'report/invoice_report_templates.xml',
        'report/invoice_report.xml',

        'data/sale_order_sequence.xml',
        'data/ir_rule.xml',

        'security/ir.model.access.csv',

        'views/assets.xml',

        'views/productions_wizard.xml',
    ],

    'application': True,
}
