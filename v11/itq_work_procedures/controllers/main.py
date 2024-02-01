from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.main import Binary


class ProcedureBinary(Binary):

    @http.route(['/web/content',
                 '/web/content/<string:xmlid>',
                 '/web/content/<string:xmlid>/<string:filename>',
                 '/web/content/<int:id>',
                 '/web/content/<int:id>/<string:filename>',
                 '/web/content/<int:id>-<string:unique>',
                 '/web/content/<int:id>-<string:unique>/<string:filename>',
                 '/web/content/<string:model>/<int:id>/<string:field>',
                 '/web/content/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='datas_fname', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw):
        response = super().content_common(xmlid=xmlid, model=model, id=id, field=field,
                                          filename=filename, filename_field=filename_field, unique=unique,
                                          mimetype=mimetype,
                                          download=download, data=data, token=token, access_token=access_token, **kw)

        if model == 'work.procedure':
            procedure = request.env['work.procedure'].browse(int(id))
            procedure.action_create_actions_tracking(
                action_type='attachment_download', attachment_name=filename)
        elif model == 'ir.attachment':
            attachment = request.env['ir.attachment'].browse(id)
            if attachment.res_model == 'work.procedure':
                request.env['work.procedure'].browse(attachment.res_id).action_create_actions_tracking(
                    action_type='attachment_download', attachment_name=attachment.datas_fname)
        return response
