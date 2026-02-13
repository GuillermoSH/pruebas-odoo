{
    'name': 'Gestión de Obras',
    'version': '1.0',
    'summary': 'Módulo básico para seguimiento de obras',
    'category': 'Operations',
    'author': 'GuillermoSH',
    'depends': ['base'],  # Dependencias necesarias, en este caso solo 'base' que es el modulo principal de Odoo
    'data': [
        'security/ir.model.access.csv', # Archivo de seguridad para definir permisos de acceso al modulo
        'views/obra_views.xml', # Localizacion de las vistas
    ],
    'installable': True,
    'application': True, # Aparece en el menu de aplicaciones directamente
}