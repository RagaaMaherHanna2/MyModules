odoo.define('itq_pos_installment_company_mgmt.PaymentScreen', function(require) {
	'use strict';

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');
	const session = require('web.session');
    const rpc = require('web.rpc');

	const InstallmentPaymentScreen = PaymentScreen =>
		class extends PaymentScreen {
			constructor() {
				super(...arguments);
			}

			async selectClient() {
				let self = this;
				if (this.currentOrder.is_paying_installment){
					return self.showPopup('ErrorPopup', {
						title: self.env._t('Not Allowed'),
						body: self.env._t('You cannot change customer of draft order.'),
					});
				} else {
					super.selectClient();
				}
			}

			async click_back(){
				let self = this;
				if(this.currentOrder.is_paying_installment){
					const { confirmed } = await this.showPopup('ConfirmPopup', {
						title: self.env._t('Cancel Payment ?'),
						body: self.env._t('Are you sure,You want to Cancel this payment?'),
					});
					if (confirmed) {
						self.env.pos.delete_current_order();
						self.showScreen('ProductScreen');
					}
				}
				else{
					self.showScreen('ProductScreen');
				}
			}

            async isInstallmentReturnedOrder(return_order_ref){
                let self = this;
                await rpc.query({
                        model: 'pos.order',
                        method: 'is_installment_returned_order',
                        args: [
                            self.id, return_order_ref
                        ],
                    }).then(function(is_installment) {
                        return is_installment;
                    });
            }

			async clickInstallmentPay(){
				let self = this;
				let order = self.env.pos.get_order();
				let return_order_ref = order.return_order_ref;
				if (order.is_paid()){
                    let orderlines = order.get_orderlines();
                    let partner_id = order.get_client();
                    if (!partner_id){
                        return self.showPopup('ErrorPopup', {
                            title: self.env._t('Unknown customer'),
                            body: self.env._t('You cannot perform installment payment.Select customer first.'),
                        });
                    }
                    else if(orderlines.length === 0){
                        return self.showPopup('ErrorPopup', {
                            title: self.env._t('Empty Order'),
                            body: self.env._t('There must be at least one product in your order.'),
                        });
                    }
                    else if(return_order_ref){
                        var paymentlines = order.get_paymentlines();
                        var installment_line =  paymentlines.some((line) => line.payment_method.is_installment_method);
                        if (installment_line){
                            return self.showPopup('ErrorPopup', {
                            title: self.env._t('Not Valid Payment method'),
                            body: self.env._t('You cannot choose installment payment method in your return order.'),
                            });
                        }
                    }
                    else{
                        var valid_order = true;
                        this.currentOrder.is_installment = true;
                        this.currentOrder.set_is_installment(true);
                        // I've set to invoice  = true to force payment create invoice
                        this.currentOrder.to_invoice = true;
                        // dont finalized order for now to be sure that the order is totally crated and invoiced
                        this.currentOrder.finalized = false;

                        // to finalize the order
                        if ((this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change()) && this.env.pos.config.iface_cashdrawer) {
                            this.env.pos.proxy.printer.open_cashbox();
                        }

                        this.currentOrder.initialize_validation_date();

                        let syncedOrderBackendIds = [];

                        try {
                            if (this.currentOrder.is_to_invoice()) {
                                syncedOrderBackendIds = await this.env.pos.push_and_invoice_order(
                                    this.currentOrder
                                );
                            } else {
                                syncedOrderBackendIds = await this.env.pos.push_single_order(this.currentOrder);
                            }
                        } catch (error) {
                            if (error.code == 700 || error.code == 701)
                                this.error = true;
                            if (error instanceof Error) {
                                throw error;
                            } else {
                                await this._handlePushOrderError(error);
                            }
                        }
                        if (syncedOrderBackendIds.length && this.currentOrder.wait_for_push_order()) {
                            const result = await this._postPushOrderResolve(
                                this.currentOrder,
                                syncedOrderBackendIds
                            );
                            if (!result) {
                                await this.showPopup('ErrorPopup', {
                                    title: 'Error: no internet connection.',
                                    body: error,
                                });
                            }
                        }

                        this.showScreen(this.nextScreen);

                        if (syncedOrderBackendIds.length && this.env.pos.db.get_orders().length) {
                            const { confirmed } = await this.showPopup('ConfirmPopup', {
                                title: this.env._t('Remaining unsynced orders'),
                                body: this.env._t(
                                    'There are unsynced orders. Do you want to sync these orders?'
                                ),
                            });
                            if (confirmed) {
                                this.env.pos.push_orders();
                            }
                        }
                    }
                }
		    }

            async _isOrderValid(isForceValidate) {
				let call_super = true;
				let self = this;
				let order = this.currentOrder;
				let return_order_ref = order.return_order_ref;
				console.log(return_order_ref)
				if (return_order_ref){
				    if (this.isInstallmentReturnedOrder(return_order_ref)){
                        await rpc.query({
                                model: 'pos.order',
                                method: 'get_order_cash_paid',
                                args: [
                                    return_order_ref
                                ],
                            }).then(function(amount) {
                                var to_return = self.env.pos.format_currency(amount);
                                var total = Math.abs(self.currentOrder.get_total_paid());
                                console.log(to_return)
                                console.log(total)
                                if (total > amount){
                                    self.showPopup('ErrorPopup', {
                                            title: self.env._t('Not Valid Return Amount'),
                                            body: self.env._t('You cannot Return Amount But only cash amount'+ to_return),
                                        });
                                    call_super = false;
                                    return false;
                                }
                            });
                    }
				}
                if(call_super){
                    return super._isOrderValid(isForceValidate);
                }
            }
	    }

        Registries.Component.extend(PaymentScreen, InstallmentPaymentScreen);

        return PaymentScreen;

    });