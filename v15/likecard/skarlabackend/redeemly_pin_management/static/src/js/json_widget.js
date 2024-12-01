/** @odoo-module **/
import AbstractField from 'web.AbstractField';
import fieldRegistry from 'web.field_registry';
const core = require('web.core');
const QWeb = core.qweb;
const { useRef, useState } = owl.hooks;
//const items = [];
var JsonFieldWidget = AbstractField.extend({
    template: "JsonFieldWidget",
    events: {
        'click .buttonSave': 'submitAttributeValues',
    },
    init: function (parent, options, targetType) {
        this._super.apply(this, arguments);
        this.targetType = targetType;
        this.state = useState({ items: JSON.parse(this.value) });
    },
    start: function () {
        this._super.apply(this, arguments);
        if (this.recordData[this.nodeOptions.currentValue]) {
            this.value = this.recordData[this.nodeOptions.currentValue]
        }
        this.state = useState({ items: JSON.parse(this.value) });
        $('div[name="json_value"').removeClass('o_field_widget');
    },
    _render: function () {
        $('div[name="json_value"').removeClass('o_field_widget');
    },
    submitAttributeValues() {
        const newValues = {};
        let isValid = true
        this.state.items.forEach(item => {
            const value = (item.type === "3") ? $(`[id=${item.id}]`).is(':checked') : $(`[id=${item.id}]`).val()
            if (item.required && !value) {
                $(`#${item.id}-validation`).removeAttr('hidden')
                isValid = false
            }
            newValues[item.id] = value
        })
        if (!isValid) return
        const jsonValue = JSON.stringify(newValues);
        this._rpc({
            model: 'product.template',
            method: 'update_voucher_secret_value',
            args: [this.record.context.active_id, jsonValue],
        }).then(function (result) {
            $(".cancel_product_fields_value_edit_tree").click()
        });
    }
})
fieldRegistry.add('json_field_widget', JsonFieldWidget);
