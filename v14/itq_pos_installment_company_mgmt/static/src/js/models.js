odoo.define('itq_pos_installment_company_mgmt.models', function(require) {
	"use strict";

    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;

	var models = require('point_of_sale.models');
	var PosDB = require("point_of_sale.DB");


	PosDB.include({
		get_unpaid_orders: function(){
			var saved = this.load('unpaid_orders',[]);
			var orders = [];
			for (var i = 0; i < saved.length; i++) {
				let odr = saved[i].data;
				if(!odr.is_paying_installment && !odr.is_installment && !odr.is_draft_order){
					orders.push(saved[i].data);
				}
				if(odr.is_paying_installment || odr.is_installment || odr.is_draft_order){
					saved = _.filter(saved, function(o){
						return o.id !== odr.uid;
					});
				}
			}
			this.save('unpaid_orders',saved);
			return orders;
		},
	});


	var PosOrder = models.Order.prototype;
	models.Order = models.Order.extend({
        initialize: function(attributes,options){
            var res = PosOrder.initialize.apply(this, arguments);
            this.is_installment = this.is_installment || false;
            this.is_paying_installment = this.is_paying_installment || false;
            return res;
        },

        init_from_JSON: function(json){
            PosOrder.init_from_JSON.apply(this,arguments);
            this.is_installment = json.is_installment;
            this.is_paying_installment = json.is_paying_installment;
        },
        export_as_JSON: function() {
            var orders = PosOrder.export_as_JSON.call(this);
            orders.is_installment = this.is_installment || false;
            orders.is_paying_installment = this.is_paying_installment || false;
            return orders;
        },
		
		set_is_installment: function(set_installment){
			this.is_installment = set_installment || false;
			this.trigger('change',this);
		},
        get_is_installment : function(){
            return this.is_installment;
        },
		set_is_paying_installment: function(is_paying_installment){
			this.is_paying_installment = is_paying_installment || false;
			this.trigger('change',this);
		},
        get_is_paying_installment : function(){
            return this.is_paying_installment;
        },

		check_paymentlines_installment: function() {
            var paymentlines = this.get_paymentlines()
            return paymentlines.some((line) => line.payment_method.is_installment_method);
        },
		is_installment_paid: function(){
            return this.get_due() <= 0 && this.check_paymentlines_installment();
        },

	});

	var posmodel_super = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        load_server_data: function(){
            var self = this;
            var progress = 0;
            var progress_step = 1.0 / self.models.length;
            var tmp = {}; // this is used to share a temporary state between models loaders

            var loaded = new Promise(function (resolve, reject) {
                function load_model(index) {
                    if (index >= self.models.length) {
                        resolve();
                    } else {
                        var model = self.models[index];
                        self.setLoadingMessage(_t('Loading')+' '+(model.label || model.model || ''), progress);

                        var cond = typeof model.condition === 'function'  ? model.condition(self,tmp) : true;
                        if (!cond) {
                            load_model(index+1);
                            return;
                        }

                        var fields =  typeof model.fields === 'function'  ? model.fields(self,tmp)  : model.fields;
                        var domain =  typeof model.domain === 'function'  ? model.domain(self,tmp)  : model.domain;
                        var context = typeof model.context === 'function' ? model.context(self,tmp) : model.context || {};
                        var ids     = typeof model.ids === 'function'     ? model.ids(self,tmp) : model.ids;
                        var order   = typeof model.order === 'function'   ? model.order(self,tmp):    model.order;
                        progress += progress_step;

                        if( model.model){
                            var params = {
                                model: model.model,
                                context: _.extend(context, self.session.user_context || {}),
                            };
                            // load is_installment_method field to pos PM
                            if (model.model === 'pos.payment.method')
                                {fields.push('is_installment_method')};

                            if (model.ids) {
                                params.method = 'read';
                                params.args = [ids, fields];
                            } else {
                                params.method = 'search_read';
                                params.domain = domain;
                                params.fields = fields;
                                params.orderBy = order;
                            }

                            self.rpc(params).then(function (result) {
                                try { // catching exceptions in model.loaded(...)
                                    Promise.resolve(model.loaded(self, result, tmp))
                                        .then(function () { load_model(index + 1); },
                                            function (err) { reject(err); });
                                } catch (err) {
                                    console.error(err.message, err.stack);
                                    reject(err);
                                }
                            }, function (err) {
                                reject(err);
                            });
                        } else if (model.loaded) {
                            try { // catching exceptions in model.loaded(...)
                                Promise.resolve(model.loaded(self, tmp))
                                    .then(function () { load_model(index +1); },
                                        function (err) { reject(err); });
                            } catch (err) {
                                reject(err);
                            }
                        } else {
                            load_model(index + 1);
                        }
                    }
                }

                try {
                    return load_model(0);
                } catch (err) {
                    return Promise.reject(err);
                }
            });

            return loaded;
        },
    });
});