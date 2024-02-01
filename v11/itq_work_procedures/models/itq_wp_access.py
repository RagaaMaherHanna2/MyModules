# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.tools import ormcache


class ItqWPMasterAccess(models.AbstractModel):
    _name = 'itq.wp.access'
    _unit_field_name = ''
    _procedure_availability_field_name = ''

    @api.model
    def _where_calc(self, domain, active_test=True):
        # OVERRIDE
        if not (self._uid == SUPERUSER_ID or self.env.context.get('skip_wp_access', False)):
            domain = domain or []
            domain = self.get_wp_access_domain(domain)
        return super(ItqWPMasterAccess, self)._where_calc(domain, active_test)

    @api.model
    def get_wp_access_domain(self, domain):
        # get user's access groups
        base_query = """
        SELECT * FROM itq_procedure_general_security_setting AS pgss
        INNER JOIN itq_procedure_security_id_user_id_rel AS psur
        ON pgss.id = psur.itq_procedure_security_id
        """
        user_where_query = """ WHERE psur.user_id = {user_id}""".format(user_id=self._uid)
        # handle is_admin
        is_admin_query = base_query + user_where_query + """
        AND pgss.is_admin = true
        """
        self.env.cr.execute(is_admin_query)
        res = self.env.cr.dictfetchall()
        department_related_domain = [(self._procedure_availability_field_name, '!=', 'secret')]
        if res:
            if not any([rec.get('access_secrets', False) for rec in res]):
                domain = (domain and ['&'] or []) + domain + department_related_domain
        else:
            # handle not is_admin
            is_not_admin_query = base_query + """
            INNER JOIN itq_procedure_security_id_admin_unit_id_rel AS psar
            ON pgss.id = psar.itq_procedure_security_id
            """ + user_where_query
            self.env.cr.execute(is_not_admin_query)
            res = self.env.cr.dictfetchall()
            if res:
                secret_admin_unit_ids = []
                not_secret_admin_unit_ids = []
                for rec in res:
                    if rec.get('admin_unit_id', False):
                        if rec.get('access_secrets', False):
                            secret_admin_unit_ids.append(rec.get('admin_unit_id'))
                        else:
                            not_secret_admin_unit_ids.append(rec.get('admin_unit_id'))
                # handle secret
                append_domain = []
                if secret_admin_unit_ids:
                    append_domain += [
                        (self._unit_field_name, 'in', secret_admin_unit_ids),
                    ]
                # handle not secret
                if not_secret_admin_unit_ids:
                    append_domain += ['&'] + department_related_domain + [
                        (self._unit_field_name, 'in', not_secret_admin_unit_ids),
                    ]
                    if secret_admin_unit_ids:
                        append_domain = ['|'] + append_domain
                # handle context allow_general_procedure_availability
                if self.env.context.get('allow_general_procedure_availability', False):
                    append_domain = (append_domain and ['|'] or []) + append_domain + [
                        (self._procedure_availability_field_name, '=', 'general')]
                if append_domain:
                    domain = (domain and ['&'] or []) + append_domain + domain
            else:
                domain = [('id', 'in', [])]
        return domain

    @api.model
    def get_department_domain(self, user=False):
        if not user:
            user = self.env.user
        domain = []
        if user.id != SUPERUSER_ID:
            base_query = """
            SELECT * FROM itq_procedure_general_security_setting AS pgss
            INNER JOIN itq_procedure_security_id_user_id_rel AS psur
            ON pgss.id = psur.itq_procedure_security_id
            """
            user_where_query = """ WHERE psur.user_id = {user_id}""".format(user_id=user.id)
            # handle is_admin
            is_admin_query = base_query + user_where_query + """
            AND pgss.is_admin = true
            """
            self.env.cr.execute(is_admin_query)
            res = self.env.cr.dictfetchall()
            if not res:
                admin_unit_ids = []
                domain = [('id', 'in', admin_unit_ids)]
                is_not_admin_query = base_query + """
                INNER JOIN itq_procedure_security_id_admin_unit_id_rel AS psar
                ON pgss.id = psar.itq_procedure_security_id
                """ + user_where_query
                self.env.cr.execute(is_not_admin_query)
                res = self.env.cr.dictfetchall()
                for rec in res:
                    if rec.get('admin_unit_id', False):
                        admin_unit_ids.append(rec.get('admin_unit_id'))
        return domain
