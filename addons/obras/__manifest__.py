{
    'name': 'Gestión de Obras',
    'version': '1.0',
    'summary': 'Módulo básico para seguimiento de obras',
    'category': 'Operations',
    'author': 'GuillermoSH',
    'depends': ['mail', 'base', 'crm'],  # Dependencias necesarias
    'data': [
        'security/ir.model.access.csv', # Archivo de seguridad para definir permisos de acceso al modulo
        'data/obras_data.xml', # Datos iniciales, como etapas del CRM
        'views/obra_views.xml',
        'views/obra_reports.xml',
        'views/report_proforma.xml', # Plantilla para la factura proforma
        'views/report_oficial.xml', # Plantilla para la factura oficial
    ],
    'installable': True,
    'application': True, # Aparece en el menu de aplicaciones directamente
}