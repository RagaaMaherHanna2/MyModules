odoo.define('itq_my_dashboard_leaves.my_dashboard_leaves', function(require){
    'use strict';

    const MyDashboard = require('itq_my_hr_dashboard.my_dashboard');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    MyDashboard.include({
        events: _.extend({}, MyDashboard.prototype.events, {
             'click .d_hr_leave_request_approve': 'leaves_to_approve',
             'click .d_leaves_request_today':'leaves_request_today',
             'click .d_leaves_request_month':'leaves_request_month',
        }),

    leaves_to_approve: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
            this.do_action({
                name: ("Leave Request"),
                type: 'ir.actions.act_window',
                res_model: 'hr.leave',
                view_mode: 'tree,form,calendar',
                views: [[false, 'list'],[false, 'form']],
                domain: [['id','in', this.login_employee.leaves_to_approve]],
                target: 'current'
            })
        },
    leaves_request_today: function(e) {
    console.log('this before', this);
        var self = this;
        var today = new Date();
        e.stopPropagation();
        e.preventDefault();
        this.do_action({
            name: ("Leaves Today"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.login_employee.leaves_today]],
            target: 'current'
        })
    },
    leaves_request_month: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var date = new Date();
        this.do_action({
            name: ("This Month Leaves"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.login_employee.leaves_this_month]],
            target: 'current'
        })
    },

    });
});