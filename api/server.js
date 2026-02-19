// server.js
const express = require('express');
const xmlrpc = require('xmlrpc');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

const ODOO_CONFIG = {
    url: 'http://localhost:8069',
    db: 'pruebas_odoo',
    username: 'email@email.com',
    password: '1234'
};

app.post('/api/create-order', async (req, res) => {
    const { customerName, customerEmail, productName, quantity, price } = req.body;
    const common = xmlrpc.createClient(`${ODOO_CONFIG.url}/xmlrpc/2/common`);
    const object = xmlrpc.createClient(`${ODOO_CONFIG.url}/xmlrpc/2/object`);

    const call = (client, method, args) => new Promise((resolve, reject) => {
        client.methodCall(method, args, (err, val) => err ? reject(err) : resolve(val));
    });

    try {
        // Autenticacion
        const uid = await call(common, 'authenticate', [ODOO_CONFIG.db, ODOO_CONFIG.username, ODOO_CONFIG.password, {}]);

        // Crear o buscar cliente si existe
        let partnerIds = await call(object, 'execute_kw', [ODOO_CONFIG.db, uid, ODOO_CONFIG.password, 'res.partner', 'search', [[['email', '=', customerEmail]]]]);
        let partnerId = partnerIds[0] || await call(object, 'execute_kw', [ODOO_CONFIG.db, uid, ODOO_CONFIG.password, 'res.partner', 'create', [{ name: customerName, email: customerEmail }]]);

        // 3. Crear Pedido (Sale Order)
        const orderId = await call(object, 'execute_kw', [ODOO_CONFIG.db, uid, ODOO_CONFIG.password, 'sale.order', 'create', [{
            partner_id: partnerId,
            order_line: [[0, 0, {
                name: productName,
                product_uom_qty: parseFloat(quantity),
                price_unit: parseFloat(price),
                // Importante: Aquí necesitarías el ID del producto real de tu Odoo
                product_id: 0 // Cambia por un ID de producto válido en tu Odoo
            }]]
        }]]);

        res.json({ success: true, orderId });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.listen(3000, () => console.log('Servidor corriendo en http://localhost:3000'));