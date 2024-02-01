odoo.define('itq_my_dashboard_leaves_transfer.my_dashboard_leaves_transfer', function(require){
    'use strict';

    const MyDashboard = require('itq_my_hr_dashboard.my_dashboard');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    MyDashboard.include({
        events: _.extend({}, MyDashboard.prototype.events, {
             'change #allocation_options':function(e) {
                e.stopPropagation();
                var $target = $(e.target);
                var value = $target.val();
                this.$('.o_year_allocation_details').empty();
                this.change_allocation_details(value);
                },
        }),

        start: async function(){
            var self = this;
            await this._super.apply(this, arguments);
            self.$('.d_leaves_allocation_details').hide();
            self.change_allocation_details('this_year');

        },

        change_allocation_details: async function(val) {
            var self = this;
            await rpc.query({
                model: 'hr.employee',
                method: 'get_employee_year_allocations',
                args: [this.login_employee.id, val, this.login_employee.first_contract_date],
            }).then(function(result){
            console.log(result)
                self.$('.o_year_allocation_details').append(QWeb.render('MyDashboardYearsAllocationsTemp', {year_allocation_details: result, option: val}));
            });
    },


    });
});