from datetime import datetime

from odoo.http import request
from odoo.tools import config


class NotificationService:

    # add notifications And Send Email for this notifications
    @staticmethod
    def Send_Notification_email(user=None, self=None):
        if self._name == 'pin.management.bank.transfer.request':
            # Check If user who Send notification is service provider or not
            if user.is_service_provider:
                merchant = self.env['res.users'].search([('id', '=', self.partner_id.user_ids.id)])
                if self.state == 'approved':
                    # Here Send Notification To Merchant
                    new_message = self.message_post(
                        author_id=self.create_uid.partner_id.id,
                        body=('This Bank Transfer has been Approved from Service Provider.'),
                        message_type='notification',
                        subtype_xmlid='redeemly_pin_management.back_accept_reject_bank_transfer',
                        notification_ids=None)
                    new_message.skarla_dashboard = True
                    if config.get('enable_email_notification') == True:
                        template = self.env.ref('redeemly_pin_management.general_bank_transfer_email_tempalte')
                        email_values = {
                            'email_from': 'noreply@skarla.com'
                        }
                        context = {
                            'name': 'Accept Bank Transfer',
                            'message': "We would like to inform you that Your Bank Transfer are Accepted by %s  With Balancing : %s" % (
                                user.partner_id.name, self.transferAmount),
                            "to_email": merchant.balance_notification_to_email}
                        template.with_context(context).send_mail(self.id)
                elif self.state == 'rejected':
                    # Here Send Notification To Merchant
                    new_message = self.message_post(
                        author_id=self.create_uid.partner_id.id,
                        body=('This Bank Transfer has been Rejected from Service Provider.'),
                        message_type='notification',
                        subtype_xmlid='redeemly_pin_management.back_accept_reject_bank_transfer',
                        notification_ids=None)
                    new_message.skarla_dashboard = True
                    if config.get('enable_email_notification') == True:
                        template = self.env.ref('redeemly_pin_management.general_bank_transfer_email_tempalte')
                        email_values = {
                            'email_from': 'noreply@skarla.com'
                        }
                        context = {
                            'name': 'Reject Bank Transfer',
                            'message': "We would like to inform you that Your Bank Transfer are Rejected by %s  With Balancing : %s" % (
                                user.partner_id.name, self.transferAmount),
                            "to_email": merchant.balance_notification_to_email}
                        template.with_context(context).send_mail(self.id)
            elif user.is_merchant:
                # Here Add Notification To Server Provider Of This Merchant
                print("welcome ########################### : ")
                print(user.create_uid.partner_id.name)
                new_message = self.message_post(
                    author_id=user.create_uid.partner_id.id,
                    body=('This Bank Transfer has been created from Merchant.'),
                    subject='This Bank Transfer has been created from Merchant.',
                    message_type='notification',
                    subtype_xmlid='redeemly_pin_management.back_request_bank_transfer',
                    notification_ids=None,
                )
                new_message.skarla_dashboard = True
                if config.get('enable_email_notification') == True:
                    template = self.env.ref('redeemly_pin_management.general_bank_transfer_email_tempalte')
                    email_values = {
                        'email_from': 'noreply@skarla.com'
                    }
                    if user.is_sub_merchant:
                        context = {
                            'name': 'Bank Transfer From Merchant',
                            'server_provider_name': user.parent_merchant.create_uid.name,
                            'message': " We would like to inform you that There  Bank Transfer Created  From Your Merchant %s  With Balancing : %s" % (
                                self.partner_id.name, self.transferAmount),
                            "to_email": user.parent_merchant.create_uid.notification_to_email}
                        template.with_context(context).send_mail(self.id)
                    else:
                        context = {
                            'name': 'Bank Transfer From Merchant',
                            'server_provider_name': user.create_uid.name,
                            'message': " We would like to inform you that There  Bank Transfer Created  From Your Merchant %s  With Balancing : %s" % (
                                self.partner_id.name, self.transferAmount),
                            "to_email": user.create_uid.notification_to_email}
                        template.with_context(context).send_mail(self.id)
        elif self._name == 'merchant.invoice.request':
            if self.state == 'success':
                new_message = self.message_post(
                    author_id=self.service_provider_id.partner_id.id,
                    body='There an  Invoice Request Success To Process .',
                    subject='There an  Invoice Request Success To Process .',
                    message_type='notification',
                    subtype_xmlid='redeemly_pin_management.back_pending_invoice_request',
                    notification_ids=None)
                new_message.skarla_dashboard = True
                if config.get('enable_email_notification'):
                    template = self.env.ref(
                        'redeemly_pin_management.pending_invoice_request_email_for_service_provider_tempalte')
                    context = {'server_base_url': config.get('server_base_url')}
                    email_values = {
                        'name': 'Merchant Invoice Request Successfully',
                        'meesage': "We want to inform you that an invoice has been issued As Successfully  for your "
                                   "Merchant %s ." % (self.merchant.partner_id.name,),
                        'email_from': 'noreply@skarla.com'
                    }
                    template.with_context(context).send_mail(self.id, email_values=email_values)
            elif self.state == 'failed':
                # Here Add Notification To Service Provider
                new_message = self.message_post(
                    author_id=self.service_provider_id.partner_id.id,
                    body=('There an  Invoice Request Failed To Process .'),
                    subject='There an  Invoice Request Failed To Process .',
                    message_type='notification',
                    subtype_xmlid='redeemly_pin_management.back_pending_invoice_request',
                    notification_ids=None)
                new_message.skarla_dashboard = True
                if config.get('enable_email_notification') == True:
                    template = self.env.ref(
                        'redeemly_pin_management.pending_invoice_request_email_for_service_provider_tempalte')
                    context = {
                        'name': 'Merchant Invoice Request Failed ',
                        'meesage': "We want to inform you that an invoice has been issued As Failled  for your Merchant %s ." % (
                            self.merchant.partner_id.name,),
                        'server_base_url': config.get('server_base_url')
                    }
                    email_values = {
                        'email_from': 'noreply@skarla.com'
                    }
                    template.with_context(context).send_mail(self.id, email_values=email_values)
        elif self._name == 'merchant.package.invites':
            if user.is_service_provider:
                new_message = self.message_post(
                    author_id=self.merchant.partner_id.id,
                    body=('Invitation On Product From Service Provider Please Check .'),
                    subject='Invitation On Product From Service Provider Please Check .',
                    message_type='notification',
                    subtype_xmlid='redeemly_pin_management.merchant_invited_on_product',
                    notification_ids=None)
                new_message.skarla_dashboard = True
                if config.get('enable_email_notification') == True:
                    template = self.env.ref(
                        'redeemly_pin_management.merchant_invited_on_product_from_service_provider_tempalte')
                    context = {
                        'server_base_url': config.get('server_base_url'),
                        'name': 'Merchant Invited On Product From Service Provider',
                        'message': "We would like to inform you that You Invited  On Product From  Service Provider %s  With This Details ." % (
                            user.partner_id.name),
                    }
                    email_values = {

                        'email_from': 'noreply@skarla.com'
                    }
                    template.with_context(context).send_mail(self.id, email_values=email_values)
        elif self._name == 'ir.cron':
            now = datetime.now()

            # new_message = self.message_post(
            #     author_id=self.create_uid.partner_id.id,
            #     body=body,
            #     subject='Cron Runner API Notification',
            #     message_type='notification',
            #     subtype_xmlid='redeemly_pin_management.cron_notify_runner',
            #     notification_ids=None)
            # new_message.skarla_dashboard = True

            template = self.env.ref(
                'redeemly_pin_management.cron_notify_runner_template')
            context = {
                'server_base_url': config.get('server_base_url'),
                'name': 'Cron Runner API Email',
                'message': ('Cron %s failed to run as scheduled so I did it at %s.' % (self.name, now)),
            }
            system_admins = self.env['res.users'].search(
                [('groups_id', 'in', self.env.ref('base.group_system').id)])

            for admin in system_admins:
                email_values = {
                    'email_from': 'noreply@skarla.com',
                    'email_to': admin.login,
                }
                template.with_context(context).sudo().send_mail(self.id, email_values=email_values)
