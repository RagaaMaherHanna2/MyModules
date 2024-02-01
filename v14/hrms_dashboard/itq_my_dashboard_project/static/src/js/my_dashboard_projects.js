odoo.define('itq_my_dashboard_project.my_dashboard_project', function(require){
    'use strict';

    const MyDashboard = require('itq_my_hr_dashboard.my_dashboard');
    var rpc = require('web.rpc');

    MyDashboard.include({

        start: async function(){
            var self = this;
            await this._super.apply(this, arguments);
            self.render_employee_projects();

        },

        render_employee_projects:function(){
            var self = this;
            var elem = this.$('.emp_projects_pie');
            rpc.query({
                model: "hr.employee",
                method: "get_employee_projects",
            }).then(function (data) {
                self.render_pie_graph(data, elem);
                });
        },
    });
});