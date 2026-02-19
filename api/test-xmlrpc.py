import os
import xmlrpc.client
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

url = os.getenv('ODOO_URL')
db = os.getenv('ODOO_DB')
username = os.getenv('ODOO_USER')
password = os.getenv('ODOO_PASSWORD')

print(f"Conectando a {url}...")

# Autenticacion del usuario
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"✅ ¡Conexión exitosa! Tu UID es: {uid}")
    
    # Crear un proxy para llamar a los metodos del modelo 'obras.obra'
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Buscar todas las obras registradas ([] significa sin filtros, es decir, todas)
    obras_ids = models.execute_kw(db, uid, password, 'obras.obra', 'search', [[]])
    print(f"📊 Tienes actualmente {len(obras_ids)} obras registradas.")

    # Creacion de una obra nueva llamando a la API
    nueva_obra_id = models.execute_kw(db, uid, password, 'obras.obra', 'create', [{
        'name': 'Obra creada desde la API',
        'coste': 5000.0,
        'aceptada': False
    }])
    print(f"🚀 Nueva obra creada con ID: {nueva_obra_id}")

else:
    print("❌ Error de autenticación. Revisa el nombre de la DB o el password.")