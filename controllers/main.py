# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class ProductConfiguratorController(http.Controller):

    @http.route(['/sale_product_configurator/show_optional_products'], type='json', auth="user", methods=['POST'])
    def show_optional_products(self, product_id, variant_values, pricelist_id, **kw):
        pricelist = self._get_pricelist(pricelist_id)
        return self._show_optional_products(product_id, variant_values, pricelist, False, **kw)

    def _show_optional_products(self, product_id, variant_values, pricelist, handle_stock, **kw):
        product = request.env['product.product'].browse(int(product_id))
        combination = request.env['product.template.attribute.value'].browse(variant_values)
        has_optional_products = product.optional_product_ids.filtered(lambda p: p._is_add_to_cart_possible(combination))
        bom = request.env['product.template']._creat_product_bom(product,combination)
        # print(product.product_tmpl_id)
        # for a in combination:
        #     print(a.product_attribute_value_id.product_id.name)
        if not has_optional_products:
            return False

        add_qty = int(kw.get('add_qty', 1))

        no_variant_attribute_values = combination.filtered(
            lambda product_template_attribute_value: product_template_attribute_value.attribute_id.create_variant == 'no_variant'
        )
        if no_variant_attribute_values:
            product = product.with_context(no_variant_attribute_values=no_variant_attribute_values)

        return request.env['ir.ui.view']._render_template("sale_product_configurator.optional_products_modal", {
            'product': product,
            'combination': combination,
            'add_qty': add_qty,
            'parent_name': product.name,
            'variant_values': variant_values,
            'pricelist': pricelist,
            'handle_stock': handle_stock,
            'bom_ids': bom,
        })

    def _get_pricelist(self, pricelist_id, pricelist_fallback=False):
        return request.env['product.pricelist'].browse(int(pricelist_id or 0))
