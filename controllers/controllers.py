from odoo import http
from odoo.http import request

class CustomProductController(http.Controller):

    @http.route('/shop/home-tendance/checkout', type='http', auth="public", website=True)
    def custom_price_product(self):
        return http.request.render('website_sale_custom.custom_product_form')

    @http.route('/shop/add_custom_product', type='http', auth="public", website=True)
    def add_custom_product(self, **kwargs):
        try:
            # Validation des entrées
            ref = kwargs.get('ref')
            description = kwargs.get('description')
            amount = kwargs.get('amount')

            if not ref or not description or not amount:
                return request.redirect('/shop/cart?error=missing_data')

            amount = float(amount)
            if amount <= 0:
                return request.redirect('/shop/cart?error=invalid_amount')

            # Récupérer l'utilisateur public si non connecté
            user = request.env.user
            if user._is_public():
                # Force l'utilisation de l'utilisateur public
                user = request.env['res.users'].sudo().search([('id', '=', request.website.user_id.id)], limit=1)

            # Récupérer la commande active ou en créer une
            order = request.website.sale_get_order(force_create=True)
            if not order:
                return request.redirect('/shop/cart?error=no_order')

            # Rechercher ou créer le produit générique
            product = request.env['product.product'].sudo().search([('default_code', '=', ref)], limit=1)
            if not product:
                # Création du produit générique
                product = request.env['product.product'].sudo().create({
                    'name': 'Produit personnalisé',
                    'default_code': ref,
                    'type': 'consu',  # Type service pour éviter les problèmes de stock
                    'list_price': amount,
                    'sale_ok': True,
                    'website_published': True,
                })

            # Ajouter le produit au panier et modifier la ligne
            order_line_id = order._cart_update(
                product_id=product.id,
                add_qty=1,
                set_qty=1,
            )['line_id']

            if order_line_id:
                # Modifier la ligne avec le prix personnalisé et la description
                order_line = request.env['sale.order.line'].sudo().browse(order_line_id)
                order_line.sudo().write({
                    'price_unit': amount,
                    'name': f"{description} (Réf: {ref})"
                })

            # Redirection vers la page de paiement
            return request.redirect('/shop/checkout')

        except Exception as e:
            return request.redirect(f'/shop/cart?error={str(e)}")')


