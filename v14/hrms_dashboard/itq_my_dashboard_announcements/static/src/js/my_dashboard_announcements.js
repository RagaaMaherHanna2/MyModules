odoo.define('itq_my_dashboard_announcements.my_dashboard_announcements', function(require){
    'use strict';

    const MyDashboard = require('itq_my_hr_dashboard.my_dashboard');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    MyDashboard.include({
        events: _.extend({}, MyDashboard.prototype.events, {
             'click .d-employee_announcements':'employee_announcements',
        }),

        employee_announcements: function(e){
                var self = this;
                e.stopPropagation();
                e.preventDefault();
                self.do_action({
                            name: ("Important Announcements"),
                            type: 'ir.actions.act_window',
                            res_model: 'hr.announcement',
                            view_mode: 'kanban,tree,form',
                            views: [[false, 'list'],[false, 'form']],
                            domain: [['id','=', this.login_employee.employee_announcements_ids]],
                            target: 'current'
                        })

            },
    });
});