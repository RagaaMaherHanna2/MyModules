odoo.define('itq_my_hr_dashboard.my_dashboard', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var session = require('web.session');
    var MyDashboard = AbstractAction.extend({
    template: 'MyDashboardMain',
    jsLibs: [
        '/itq_my_hr_dashboard/static/src/js/lib/d3.min.js'
    ],
    cssLibs: [
        '/itq_my_hr_dashboard/static/src/css/lib/nv.d3.css'
    ],
    events: {
             'click .hr_payslip':'hr_payslip',
             'click .hr_contract':'hr_contract',
             'click .d_employee_ex_docs':'employee_ex_docs',
             'click .d_service_dashboard':'service_dashboard',
             'click .d_custom_dashboard':'custom_dashboard',
             },

    init: function () {
            this._super.apply(this, arguments);
        },

    willStart: function(){
        var self = this;
        this.login_employee = {};
        return this._super()
        .then(function() {
            var def1 =  rpc.query({
                    model: 'hr.employee',
                    method: 'get_user_employee_details'
                }).then(function(result) {
                    self.login_employee =  result[0];
                });

        return $.when(def1);
        });
    },

    start: function() {
        var self = this;
        this.set("title", 'My Profile');
        if (this.login_employee){
            return this._super.apply(this, arguments).then(function() {
                self.$('.o_hr_dashboard').append(QWeb.render('MyDashboardTemp', {widget: self}));
                self.render_employee_departments();
                self.render_employee_jobs();
                self.$el.parent().addClass('oe_background_grey');
            });
        }
        else{
            return this._super().then(function() {
                self.$('.o_hr_dashboard').append(QWeb.render('EmployeeWarning', {widget: self}));
            });
        }

    },

    // Events
    hr_payslip: function(ev){
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                name: ("Employee Payslips"),
                type: 'ir.actions.act_window',
                res_model: 'hr.payslip',
                view_mode: 'tree,form,calendar',
                views: [[false, 'list'],[false, 'form']],
                domain: [['employee_id','=', this.login_employee.id]],
                target: 'current'
            });
        },
    hr_contract: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            self.do_action({
                        name: ("Contracts"),
                        type: 'ir.actions.act_window',
                        res_model: 'hr.contract',
                        view_mode: 'kanban,tree,form',
                        views: [[false, 'list'],[false, 'form']],
                        domain: [['employee_id','=', this.login_employee.id]],
                        target: 'current'
                    })

        },
    employee_ex_docs: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        this.do_action({
            name: ("Expiring Documents within 2 Months"),
            type: 'ir.actions.act_window',
            res_model: 'itq.document',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','=', this.login_employee.expiring_docs_ids]],
            target: 'current'
        })
    },

    service_dashboard: function(ev){
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                    type: "ir.actions.client",
                    tag: 'itq_services_dashboard',
            });
        },
    custom_dashboard: function(ev){
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            this.do_action({
                    type: "ir.actions.client",
                    tag: 'ks_dashboard_ninja',
                    params: {'ks_dashboard_id': this.login_employee.ks_my_default_dashboard_board},
            });
        },

    render_pie_graph:function(data, elem){
        var w = 200;
        var h = 200;
        var r = h/2;
        var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
        '#ffa433', '#ffc25b', '#f8e54b'];
        var color = d3.scale.ordinal().range(colors);
        var segColor = {};
        var vis = d3.select(elem[0]).append("svg:svg").data([data]).attr("width", w).attr("height", h).append("svg:g").attr("transform", "translate(" + r + "," + r + ")");
        var pie = d3.layout.pie().value(function(d){return d.value;});
        var arc = d3.svg.arc().outerRadius(r);
        var arcs = vis.selectAll("g.slice").data(pie).enter().append("svg:g").attr("class", "slice");
        arcs.append("svg:path")
            .attr("fill", function(d, i){
                return color(i);
            })
            .attr("d", function (d) {
                return arc(d);
            });

        var legend = d3.select(elem[0]).append("table").attr('class','legend');

        // create one row per segment.
        var tr = legend.append("tbody").selectAll("tr").data(data).enter().append("tr");

        // create the first column for each segment.
        tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
            .attr("width", '16').attr("height", '16')
            .attr("fill",function(d, i){ return color(i) });

        // create the second column for each segment.
        tr.append("td").text(function(d){ return d.label;});

        // create the third column for each segment.
        tr.append("td").attr("class",'legendFreq')
            .text(function(d){ return d.value;});

    },

    render_employee_departments:function(){
        var self = this;
        var elem = this.$('.emp_departments_pie');
        rpc.query({
            model: "hr.employee",
            method: "get_employee_departments",
        }).then(function (data) {
            self.render_pie_graph(data, elem);
        });

    },

    render_employee_jobs:function(){
        var self = this;
        var elem = this.$('.emp_jobs_pie');
        rpc.query({
            model: "hr.employee",
            method: "get_employee_jobs",
        }).then(function (data) {
            self.render_pie_graph(data, elem);
            });
    },

    });

    core.action_registry.add("my_dashboard", MyDashboard);
    return MyDashboard;
});