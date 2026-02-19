// server.js
const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
app.use(express.json());
app.use(cors());

const ODOO_CONFIG = {
    url: 'http://localhost:8069/jsonrpc',
    db: 'pruebas_odoo',
    username: 'email@email.com',
    apiKey: 'b554a101e5c04cae67140a04b038794ff31c8135',
};

async function odooCall(service, method, args) {
    const payload = {
        jsonrpc: "2.0",
        method: "call",
        params: {
            service: service,
            method: method,
            args: args
        },
        id: Date.now()
    };

    const response = await axios.post(ODOO_CONFIG.url, payload);
    
    if (response.data.error) {
        throw new Error(JSON.stringify(response.data.error));
    }
    
    return response.data.result;
}

app.post('/api/create-order', async (req, res) => {
    const { customerName, customerEmail, productName, quantity, price, productId } = req.body;

    try {
        // Autenticacion
        const uid = await odooCall('common', 'authenticate', [
            ODOO_CONFIG.db,
            ODOO_CONFIG.username,
            ODOO_CONFIG.apiKey,
            {}
        ]);

        if (!uid) return res.status(401).json({ error: "Auth failed" });

        // Crear o buscar cliente si existe
        const partnerIds = await odooCall('object', 'execute_kw', [
            ODOO_CONFIG.db, uid, ODOO_CONFIG.apiKey,
            'res.partner', 'search', [[['email', '=', customerEmail]]]
        ]);

        let partnerId = partnerIds[0];
        if (!partnerId) {
            partnerId = await odooCall('object', 'execute_kw', [
                ODOO_CONFIG.db, uid, ODOO_CONFIG.apiKey,
                'res.partner', 'create', [{ name: customerName, email: customerEmail }]
            ]);
        }

        // Crear Pedido (sale.order)
        const orderId = await odooCall('object', 'execute_kw', [
            ODOO_CONFIG.db, uid, ODOO_CONFIG.apiKey,
            'sale.order', 'create', [{
                partner_id: partnerId,
                order_line: [[0, 0, {
                    name: productName,
                    product_uom_qty: parseFloat(quantity),
                    price_unit: parseFloat(price),
                    product_id: productId || 1
                }]]
            }]]);

        res.json({ success: true, orderId });
    } catch (error) {
        console.error("Odoo Error:", error.message);
        res.status(500).json({ success: false, error: error.message });
    }
});

app.listen(3000, () => console.log('Server Axios-Odoo en puerto 3000'));