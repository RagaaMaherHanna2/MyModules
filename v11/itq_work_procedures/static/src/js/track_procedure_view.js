odoo.define('itq_work_procedures.track_procedure_view', function(require) {

    var ListController = require('web.ListController');

    ListController = ListController.include({
            _onOpenRecord: function (event) {
                this._super.apply(this, arguments);
                    event.stopPropagation();
                    var record = this.model.get(event.data.id, {raw: true});
                    if (this.modelName === 'work.procedure'){
                        this._rpc({
                                    model: 'work.procedure',
                                    method: 'action_create_actions_tracking',
                                    args: [record.res_id, 'view'],
                                });
                    }
            },

    });
});