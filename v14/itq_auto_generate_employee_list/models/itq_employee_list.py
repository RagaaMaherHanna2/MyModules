# -*- coding:utf-8 -*-
import json

from lxml import etree

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ItqEmployeeList(models.Model):
    _inherit = 'itq.employee.list'

    list_for = fields.Selection([('default', 'Default'), ('project', 'Project'),
                                 ('department', 'Department'), ])

    project_id = fields.Many2one('project.project')
    department_id = fields.Many2one('hr.department')
    active = fields.Boolean('Active', default=True)

    def action_archive(self):
        if self.env['ir.config_parameter'].sudo().get_param(
                'itq_auto_generate_employee_list.is_auto_generated_list'):
            raise ValidationError(_("You Can't Archive Employee List With auto generate lists feature"))
        return super(ItqEmployeeList, self).action_archive()

    def action_unarchive(self):
        if self.env['ir.config_parameter'].sudo().get_param(
                'itq_auto_generate_employee_list.is_auto_generated_list'):
            raise ValidationError(_("You Can't UnArchive Employee List With auto generate lists feature"))
        return super(ItqEmployeeList, self).action_unarchive()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type in ['form', 'tree'] and self.env['ir.config_parameter'].sudo().get_param(
                'itq_auto_generate_employee_list.is_auto_generated_list'):
            for node in doc.xpath("//form"):
                node.set("create", 'false')
                node.set("delete", 'false')
                node.set("archive", 'false')
                node.set("unarchive", 'false')

            for node in doc.xpath("//tree"):
                node.set("create", 'false')
                node.set("delete", 'false')
                node.set("archive", 'false')
                node.set("unarchive", 'false')

            for node in doc.xpath("//tree/field[@name='employees_count']"):
                node.addnext(etree.Element('field', {'name': 'list_for'}))

            if view_type == 'form':
                for node in doc.xpath("//form/header/button[@name='get_employee_list_wizard']"):
                    modifiers = {}
                    if node.get("modifiers"):
                        modifiers = json.loads(node.get("modifiers"))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))

                employees_tree_arch = etree.XML(res['fields']['employee_ids']['views']['tree']['arch'])
                for button_node in employees_tree_arch.xpath("//button[@name='remove_employee_from_list']"):
                    modifiers = {}
                    if button_node.get("modifiers"):
                        modifiers = json.loads(button_node.get("modifiers"))

                    modifiers['invisible'] = True
                    button_node.set("modifiers", json.dumps(modifiers))

                res['fields']['employee_ids']['views']['tree']['arch'] = etree.tostring(employees_tree_arch)

                for node in doc.xpath("//form/sheet/group/field[@name='employees_count']"):
                    modifiers = {}
                    node.addnext(etree.Element('field', {'name': 'list_for'}))
                    modifiers['invisible'] = [('list_for', '!=', 'project')]
                    node.addnext(etree.Element('field', {'name': 'project_id',
                                                         'modifiers': json.dumps(modifiers)}))

                    modifiers['invisible'] = [('list_for', '!=', 'department')]
                    node.addnext(etree.Element('field', {'name': 'department_id',
                                                         'modifiers': json.dumps(modifiers)}))

        res['arch'] = etree.tostring(doc)
        return res
