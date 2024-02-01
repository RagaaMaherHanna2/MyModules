odoo.define('itq_my_dashboard_time_management.my_dashboard_time_management', function(require){
    'use strict';
    const MyDashboard = require('itq_my_hr_dashboard.my_dashboard');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    MyDashboard.include({
        events: _.extend({}, MyDashboard.prototype.events, {
             'click .d_employee_working_times':'working_times',
             'click .d_employee_rest_days':'rest_days',
        }),

        start: async function(){
            var self = this;
            await this._super.apply(this, arguments);
            self.render_employee_attendance_pie();
        },

        render_employee_attendance_pie:function(){
            var self = this;
            var data = [];
            var elem = this.$('.emp_attendance_pie');
            if (self.login_employee){data = self.login_employee.attendance_data;} else{data= false}
            console.log(data)
            self.render_pie_graph(data, elem);
        },

        working_times: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                        name: ("Working Times"),
                        type: 'ir.actions.act_window',
                        res_model: 'resource.calendar',
                        view_mode: 'kanban,tree,form',
                        views: [[false, 'list'],[false, 'form']],
                        domain: [['id','=', this.login_employee.working_time_ids]],
                        target: 'current'
                    })

            },
        rest_days: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                        name: ("Rest Days"),
                        type: 'ir.actions.act_window',
                        res_model: 'itq.rest.days.assignation.line',
                        view_mode: 'kanban,tree,form',
                        views: [[false, 'list'],[false, 'form']],
                        domain: [['id','=', this.login_employee.rest_days_ids]],
                        target: 'current'
                    })

            },

    });
});