/** @odoo-module **/

import publicWidget from 'web.public.widget';
import core from 'web.core';

var QWeb = core.qweb;
var _t = core._t;

/**
 * This Widget is responsible of displaying the visitor inputs when adding a new visitor or when updating an
 * existing one. W
 */
var VisitorFormWidget = publicWidget.Widget.extend({
    template: 'visitor.form.input',
    events: {
        'click .o_validate_visitor': '_validateVisitor',
        'click .o_cancel_visitor': '_cancelValidation',
        'click .o_visitor_info': '_addVisitorInfo',
//        'click .o_wslides_js_quiz_remove_answer': '_removeAnswerLine',
//        'click .o_wslides_js_quiz_remove_answer_comment': '_removeAnswerLineComment',
//        'change .o_wslides_js_quiz_answer_comment > input[type=text]': '_onCommentChanged'
    },

    /**
     * @override
     * @param parent
     * @param options
     */
    init: function (parent, options) {
//        this.$editedvisitor = options.editedvisitor;
        this.expectedNumber = options.expectedNumber || 0;
        this.update = options.update;
        this.sequence = options.sequence;
        this.visitor = options.visitor || {};
//        this.slideId = options.slideId;
        this._super.apply(this, arguments);
    },

    /**
     * @override
     * @returns {*}
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.$('.o_visitor_input input').focus();
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------


    /**
     * Removes an answer line. Can't remove the last answer line.
     * @param ev
     * @private
     */
    _removeAnswerLine: function (ev) {
        if (this.$('.o_wslides_js_quiz_answer').length > 1) {
            $(ev.currentTarget).closest('.o_wslides_js_quiz_answer').remove();
        }
    },

    /**
     * Handler when user click on 'Save' or 'Update' buttons.
     * @param ev
     * @private
     */
    _validateVisitor: function (ev) {
        this._createOrUpdateVisitor({
            update: $(ev.currentTarget).hasClass('o_visitor_update'),
        });
    },

    /**
     * Handler when user click on the 'Cancel' button.
     * Calls a method from slides_course_quiz.js widget
     * which will handle the reset of the visitor display.
     * @private
     */
    _cancelValidation: function () {

        console.log('_cancelValidation');
        this.trigger_up('reset_display', {
            VisitorFormWidget: this,
        });
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * RPC call to create or update a visitor.
     * Triggers method from slides_course_quiz.js to
     * correctly display the Visitor Info.
     * @param options
     * @private
     */
    _createOrUpdateVisitor: async function (options) {
        var $form = this.$('form');
        console.log('_createOrUpdateVisitor')

        if (this._isValidForm($form)) {
            var values = this._serializeForm($form);
            var renderedvisitor = await this._rpc({
                route: '/request/visitor/add_or_update',
                params: values
            });
                    console.log(renderedvisitor)

//
            if (renderedvisitor) {
            this.trigger_up('display_updated_visitor', {
                    newvisitorRenderedTemplate: renderedvisitor,
                    $editedvisitor: this.$editedvisitor,
                    VisitorFormWidget: this,
                });
            }
// else if (options.update) {
//                this.$('.o_wslides_js_quiz_validation_error').addClass('d-none');
//                this.trigger_up('display_updated_visitor', {
//                    newvisitorRenderedTemplate: renderedvisitor,
//                    $editedvisitor: this.$editedvisitor,
//                    VisitorFormWidget: this,
//                });
//            } else {
//                this.$('.o_wslides_js_quiz_validation_error').addClass('d-none');
//                this.trigger_up('display_created_visitor', {
//                    newvisitorRenderedTemplate: renderedvisitor,
//                    VisitorFormWidget: this
//                });
//            }
//        } else {
//            this.$('.o_wslides_js_quiz_validation_error')
//                .removeClass('d-none')
//                .find('.o_wslides_js_quiz_validation_error_text')
//                .text(_t('Please fill in the visitor'));
//            this.$('.o_wslides_quiz_visitor input').focus();
        }
    },

    /**
     * Check if the visitor has been filled up
     * @param $form
     * @returns {boolean}
     * @private
     */
    _isValidForm: function($form) {
//        TODO to check mobile and email also
        return $form.find('.o_visitor input[type=text]').val().trim() !== "";
    },

    _serializeForm: function ($form) {
        return {
            'existing_visitor_id': this.$el.data('id'),
            'sequence': this.sequence,
            'name': $form.find('.o_visitor_name_value').val(),
            'mobile': $form.find('.o_visitor_mobile_value').val(),
            'email': $form.find('.o_visitor_email_value').val(),
        };
    },

});

export default VisitorFormWidget;
