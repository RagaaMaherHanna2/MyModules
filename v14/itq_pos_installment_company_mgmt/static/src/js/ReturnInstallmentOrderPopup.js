odoo.define('itq_pos_installment_company_mgmt.ReturnInstallmentOrderPopup', function(require) {
	'use strict';

	const { useExternalListener } = owl.hooks;
	const PosComponent = require('point_of_sale.PosComponent');
	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { useState } = owl.hooks;
    const rpc = require('web.rpc');
	const ReturnOrderPopup = require('pos_orders_all.ReturnOrderPopup');

	const ReturnInstallmentOrderPopup = ReturnOrderPopup =>
		class extends ReturnOrderPopup {
			constructor() {
				super(...arguments);
			}

			async do_returnOrder(){
                console.log('im in itq_pos_installment_company_mgmt')
                let self = this;
                let selectedOrder = self.env.pos.get_order();
                let orderlines = self.props.orderlines;
                let order = self.props.order;
                if(order.is_installment){
                await rpc.query({
                    model: 'pos.order',
                    method: 'is_fully_installment_paid',
                    args: [
                        self.id, order.id
                    ],
                }).then(function(res) {
                if (res){
                    return self.showPopup('ErrorPopup', {
                            title: self.env._t('Is instalment paid'),
                            body: self.env._t('You cannot return order is paid with instalment method!'),
                        });
                }
                });

                let partner_id = false
                let client = false
                if (order && order.partner_id != null){
                    partner_id = order.partner_id[0];
                    client = self.env.pos.db.get_partner_by_id(partner_id);
                }
                let return_products = {};
                let exact_return_qty = {};
                let exact_entered_qty = {};

                let list_of_qty = $('.entered_item_qty');
                $.each(list_of_qty, function(index, value) {
                    let entered_item_qty = $(value).find('input');
                    let qty_id = parseFloat(entered_item_qty.attr('qty-id'));
                    let line_id = parseFloat(entered_item_qty.attr('line-id'));
                    let entered_qty = parseFloat(entered_item_qty.val());
                    let returned_qty = parseFloat(entered_item_qty.attr('return-qty'));
                    exact_return_qty = qty_id;
                    exact_entered_qty = entered_qty || 0;
                    let remained = qty_id - returned_qty;

                    if(remained < entered_qty){
                        alert("Cannot Return More quantity than purchased");
                        return;
                    }
                    else{
                        if(!exact_entered_qty){
                            return;
                        }
                        else if (exact_return_qty >= exact_entered_qty){
                          return_products[line_id] = entered_qty;
                        }
                        else{
                            alert("Cannot Return More quantity than purchased");
                            return;
                        }
                    }
                });

                let invalid_prod = false;
                $.each( return_products, function( key, value ) {
                    orderlines.forEach(function(ol) {
                        if(ol.id == key && value > 0){
                            let product = self.env.pos.db.get_product_by_id(ol.product_id[0]);

                            if(product){
                                selectedOrder.add_product(product, {
                                    quantity: - parseFloat(value),
                                    price: ol.price_unit,
                                    discount: ol.discount,
                                    pass_validation: true,
                                });
                                selectedOrder.set_return_order_ref(ol.order_id[0]);
                                selectedOrder.selected_orderline.set_original_line_id(ol.id);
                            }else{
                                invalid_prod = true;
                                alert("Please configure Product:( "+ol.product_id[1]+" ) for POS.")
                            }
                        }
                    });
                });

                selectedOrder.set_client(client);
                self.props.resolve({ confirmed: true, payload: null });
                self.trigger('close-popup');
                self.trigger('close-temp-screen');

            }
            else {
                super.do_returnOrder();
                }
		}
	}

	Registries.Component.extend(ReturnOrderPopup, ReturnInstallmentOrderPopup);

	return ReturnOrderPopup;
});
