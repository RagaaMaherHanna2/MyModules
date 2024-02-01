/** @odoo-module **/

var core = require('web.core');
var publicWidget = require('web.public.widget');
var rpc = require('web.rpc');
var QWeb = core.qweb;

import { _lt } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";

publicWidget.registry.visitRequestDetailsWidget = publicWidget.Widget.extend({
    /*
        this js file handles form submission and inputs changes
        1- change inputs visibility upon user (visit and request type) selection
        2- serialize the form inputs after validate them taking in consideration when update form only changed values
            are validated and taken (see _on_field_value_change event)
    */
    selector: '.o_visit_request_details',
    events: {
        'change .o_request_type': '_on_request_type_change',
        'change .o_visitor_type': '_on_visitor_type_change',
        'change .o_visit_type': '_on_visit_type_change',
        'change .o_visit_department': '_on_visit_department_change',
        'change .o_document_visit': '_on_document_visit_change',

        // trigger only changed inputs
        'change .o_field_value': '_on_field_value_change',

        // visitors handlers
        'click .o_add_visitors': '_on_add_visitors_click',
        'click .o_add_visitor': '_on_add_visitors_click',
        'click .o_remove_visitor': '_removeVisitorLine',

        // form submission
        'click button[name="submit"]': '_onSubmit',
        'click button[name="update"]': '_onUpdate',

    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    _on_request_type_change: function (ev) {
        document.getElementById('photoshoot_attraction').value = '';
        document.getElementById('visit_attraction').value = '';
        if($(ev.currentTarget).val() == 'visit') {
            this.$el.find('.o_visit_attraction').removeClass('o_hidden');
            this.$el.find('.o_photoshoot_attraction').addClass('o_hidden');
        }
        else if($(ev.currentTarget).val() == 'photoshoot') {
            this.$el.find('.o_photoshoot_attraction').removeClass('o_hidden');
            this.$el.find('.o_visit_attraction').addClass('o_hidden');
        }
        else {
            this.$el.find('.o_photoshoot_attraction').addClass('o_hidden');
            this.$el.find('.o_visit_attraction').addClass('o_hidden');
        }
    },

    _on_field_value_change: function (ev) {
        if (!$(ev.currentTarget).hasClass('o_has_changed')) {$(ev.currentTarget).addClass('o_has_changed');}
        if ($(ev.currentTarget).hasClass('o_visitor_name_value') || $(ev.currentTarget).hasClass('o_visitor_email_value') || $(ev.currentTarget).hasClass('o_visitor_mobile_value')) {
            $(ev.currentTarget).closest('.o_existing_visitor_line').addClass('o_has_changed')
        }
    },

    _on_visit_type_change: function (ev) {
        document.getElementById('photoshoot_attraction').value = '';
        document.getElementById('visit_attraction').value = '';
        document.getElementById('visit_department').value = '';
        if($(ev.currentTarget).val() == 'meeting') {
            this.$el.find('.o_attraction_div').addClass('o_hidden');
            this.$el.find('.o_department_div').removeClass('o_hidden');
        }
        else{
         this.$el.find('.o_department_div').addClass('o_hidden');
         this.$el.find('.o_attraction_div').removeClass('o_hidden');

        }
    },

    _on_visitor_type_change: function (ev) {
        let orgDiv = this.$el.find('.o_visitor_organization');
        if($(ev.currentTarget).val() == 'organization') {
            orgDiv.removeClass('o_hidden');
        } else {
            orgDiv.value = '';
            orgDiv.addClass('o_hidden');
        }
    },

    get_department_data: function (depId) {
        var self = this;
        const department_data = rpc.query({
            model: "hr.department",
            method: 'read',
            args: [parseInt(depId), ['resource_calendar_id', 'is_research_department']],
        });
        return department_data
    },

    async _on_visit_department_change(ev) {
        var depId = $(ev.currentTarget).val();
        const depData = await this.get_department_data(depId)
        let resDiv = this.$el.find('.o_research_div');
        if(depData[0]['is_research_department']) {
            resDiv.removeClass('o_hidden');
        } else {
            document.getElementById('research_type').value = '';
            document.getElementById('research_topic').value = '';
            resDiv.addClass('o_hidden');
        }
    },

    _on_document_visit_change: function (ev) {
        let dType = this.$el.find('.o_documentation_type');
        if($(ev.currentTarget)[0].checked) {
            dType.removeClass('o_hidden');
        } else {
            document.getElementById('documentation_type_id').value = '';
            dType.addClass('o_hidden');
        }
    },

    _on_add_visitors_click: function(ev) {
        $(ev.currentTarget).closest('.o_add_visitors_div_btn').after(QWeb.render('visitor.line'));
//        TODO to handel validation on visitors creation
//        var expectedNumber = document.getElementById('expected_number_id').value;
//        while (expectedNumber > 0) {
//          expectedNumber--;
//        }
    },

    _removeVisitorLine: function (ev) {
        // The new line
        if (this.$('.o_visitor').length > 1) {
            $(ev.currentTarget).closest('.o_visitor').remove();
        }
        // The existing line
        if (this.$('.o_existing_visitor_line').length > 0) {
            var line_id = $(ev.currentTarget).closest('.o_visitor_id_value').val()
            $(ev.currentTarget).closest('.o_existing_visitor_line').addClass('o_removed_line');
            $(ev.currentTarget).closest('.o_existing_visitor_line').hide();
        }
    },

    //--------------------------------------------------------------------------
    // Form Submission
    //--------------------------------------------------------------------------

    _validateFormInput: function (inputField) {
        if ($(inputField).hasClass('o_existing_visitor_line')) {
            // pass
        }
        else if (!$(inputField)[0].checkValidity()) {
            $(inputField).addClass('is-invalid');
            $(inputField).popover({content: $(inputField)[0].validationMessage, trigger: 'hover', container: 'body', placement: 'top'});
            this.displayNotification({
                message: sprintf(_lt($(inputField)[0].validationMessage)),
                type: 'danger',
            });
            return false;
        }
        else if ($(inputField)[0].name == 'visit_date_from' || $(inputField)[0].name == 'visit_date_to') {
            // 2- Check dates Validity
            if (!this._dates_validation()) return false;
        }
        else {
            if ($(inputField).hasClass('is-invalid')) {
                $(inputField).removeClass('is-invalid').popover('dispose');
            }
        }
        return true;
    },

    _dates_validation: function () {
        var date_from = document.getElementById('visit_date_from_id');
        var date_to = document.getElementById('visit_date_to_id');
        if (date_from.value > date_to.value) {
            this.displayNotification({
                message: sprintf(_lt('Visit Date To Must be grater than Date From')),
                type: 'danger',
            });
            return false;
        }
        return true;
    },

     async _serializeForm (submission_type) {
        var $form = this.$('form');
        var values = {};
        // pass inputs upon submission_type if create all inputs else only have changed
        if (submission_type == 'create') {var formInputs = $form.find('.o_field_value')}
        else {var formInputs = $form.find('.o_has_changed')}
        for (let inputField of $(formInputs)) {
            // 1- handel attachment input
            if ($(inputField).attr("name") == 'visit_letter_id') {
                const file = document.getElementById('visit_letter_id').files[0];
                const convertBase64 = (file) => {
                    return new Promise((resolve, reject) => {
                        const fileReader = new FileReader();
                        fileReader.readAsDataURL(file);

                        fileReader.onload = () => {
                            resolve(fileReader.result);
                        };

                        fileReader.onerror = (error) => {
                            reject(error);
                        };
                    });
                }
                var fileString = await convertBase64(file);
                /* this function returns (data type and text Base64str) so we have to split unneeded part (data type)
                -- (see console.log(fileString) before splitting */
                fileString = fileString.split(";base64,")[1]
                values['file_name'] = file.name;
                values[$(inputField).attr("name")] = fileString;
            }
            // 2- Check Input Validity
            else if(this._validateFormInput(inputField)) {
                values[$(inputField).attr("name")] = $(inputField).val();
            }
            else return false;
        }

        var visitor_lines = []
        // 3-Create Visitors lines
        var new_lines = $form.find('.o_visitor_line_data');
        if (new_lines) {
            for (let visitorLine of $(new_lines)) {
                visitor_lines.push([0, 0, {'name': $(visitorLine).find('.o_visitor_name_value').val(),
                                           'mobile': $(visitorLine).find('.o_visitor_mobile_value').val(),
                                           'email': $(visitorLine).find('.o_visitor_email_value').val(),
                                           }]);
            }
        }
        // 4-Update existing Visitors lines
        var existing_lines = [$form.find('.o_existing_visitor_line')];
        existing_lines = existing_lines.filter((l) => $(l).hasClass('o_has_changed')); // return only changed lines
        if (existing_lines) {
            for (let visitorLine of $(existing_lines)) {
                var line_id = $(visitorLine).find('.o_visitor_id_value').val()
                visitor_lines.push([1, parseInt(line_id), {'name': $(visitorLine).find('.o_visitor_name_value').val(),
                                                           'mobile': $(visitorLine).find('.o_visitor_mobile_value').val(),
                                                           'email': $(visitorLine).find('.o_visitor_email_value').val(),
                                                           }]);
            }
        }
        // 5-Delete removed lines
        var removed_lines = $form.find('.o_removed_line');
        if (removed_lines) {
            for (let visitorLine of $(removed_lines)) {
            var line_id = $(visitorLine).find('.o_visitor_id_value').val()
                visitor_lines.push([2, parseInt(line_id), 0]);
            }
        }
        if (visitor_lines) {values['visitor_ids'] = visitor_lines}
        return values;
    },

     async _onUpdate(ev) {
        ev.preventDefault();
        var $form = this.$('form');
        var req_values = await this._serializeForm('update');
        if (req_values) {
            var crf_token = $form.find('.o_token').val();
            var visit_request_id = $form.find('.o_visit_req').val();
            var url = await this._route_request(req_values, crf_token, '/visit_request_update', visit_request_id);
            if (url) {window.location.replace(url);}
        }

     },

     async _onSubmit(ev) {
        ev.preventDefault();
        var $form = this.$('form');
        var req_values = await this._serializeForm('create');
        if (req_values) {
            var crf_token = $form.find('.o_token').val();
            var url = await this._route_request(req_values, crf_token, '/visit_request_create');
            if (url) {window.location.replace(url);}
        }
    },

    _route_request: function (req_values, crf_token, route, visit_request_id=null){
        return this._rpc({
            route: route,
            params: {req_values, crf_token, visit_request_id},
        });

export const visitRequestDetailsWidget = publicWidget.registry.visitRequestDetailsWidget;