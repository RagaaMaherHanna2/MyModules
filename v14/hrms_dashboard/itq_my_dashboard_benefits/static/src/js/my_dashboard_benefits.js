odoo.define('itq_my_dashboard_benefits.my_dashboard_benefits', function(require){
    'use strict';

    const MyDashboard = require('itq_my_hr_dashboard.my_dashboard');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    MyDashboard.include({
        events: _.extend({}, MyDashboard.prototype.events, {
             'click .valuable_benefits':'valuable_benefits',
             'click .non_valuable_benefits':'non_valuable_benefits',
             'click .benefit_change_requests':'benefit_change_requests',
             'click .non_periodical_benefit_requests':'non_periodical_benefit_requests',
        }),

        valuable_benefits: function(e){
                var self = this;
                e.stopPropagation();
                e.preventDefault();
                self.do_action({
                            name: ("Valuable Benefits"),
                            type: 'ir.actions.act_window',
                            res_model: 'itq.hr.contract.benefit',
                            view_mode: 'kanban,tree,form',
                            views: [[false, 'list'],[false, 'form']],
                            domain: [['id','=', this.login_employee.valuable_benefit_ids]],
                            target: 'current'
                        })

            },
        non_valuable_benefits: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                        name: ("Non Valuable Benefits"),
                        type: 'ir.actions.act_window',
                        res_model: 'itq.hr.contract.benefit',
                        view_mode: 'kanban,tree,form',
                        views: [[false, 'list'],[false, 'form']],
                        domain: [['id','=', this.login_employee.non_valuable_benefit_ids]],
                        target: 'current'
                    })

        },
        benefit_change_requests: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                        name: ("Benefits Change Requests"),
                        type: 'ir.actions.act_window',
                        res_model: 'itq.contract.benefit.change.request',
                        view_mode: 'kanban,tree,form',
                        views: [[false, 'list'],[false, 'form']],
                        domain: [['id','=', this.login_employee.benefit_change_request_ids]],
                        target: 'current'
                    })

        },
        non_periodical_benefit_requests: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                        name: ("Non-periodical Benefits Requests"),
                        type: 'ir.actions.act_window',
                        res_model: 'itq.non.periodical.benefit.request',
                        view_mode: 'kanban,tree,form',
                        views: [[false, 'list'],[false, 'form']],
                        domain: [['id','=', this.login_employee.non_periodical_benefit_request_ids]],
                        target: 'current'
                    })

        },
    });
});