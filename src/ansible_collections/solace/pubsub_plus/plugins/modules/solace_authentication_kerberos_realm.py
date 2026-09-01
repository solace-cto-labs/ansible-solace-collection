#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2026, Solace Corporation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: solace_authentication_kerberos_realm
short_description: kerberos realm
description:
- "Configure an Authentication Kerberos Realm object on a Message Vpn. Allows addition, removal and configuration of objects in an idempotent manner."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  createMsgVpnAuthenticationKerberosRealm"
options:
  name:
    description: The name of the Kerberos Realm. Maps to 'kerberosRealmName' in the API.
    required: true
    type: str
    aliases: [kerberos_realm, kerberos_realm_name]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace.pubsub_plus.solace_get_authentication_kerberos_realms
author:
- Paulus Gunadi (@pjgunadi)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
module_defaults:
  solace_authentication_kerberos_realm:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
- name: add
  solace_authentication_kerberos_realm:
    name: EXAMPLE.COM
    settings:
      kdcAddress: "kdc.example.com"
    state: present

- name: update
  solace_authentication_kerberos_realm:
    name: EXAMPLE.COM
    settings:
      kdcAddress: "kdc2.example.com"
    state: present

- name: remove
  solace_authentication_kerberos_realm:
    name: EXAMPLE.COM
    state: absent
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
    returned: success
msg:
    description: The response from the HTTP call in case of error.
    type: dict
    returned: error
rc:
    description: Return code. rc=0 on success, rc=1 on error.
    type: int
    returned: always
    sample:
        success:
            rc: 0
        error:
            rc: 1
'''

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys  # pylint: disable=unused-import
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceAuthenticationKerberosRealmTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'kerberosRealmName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['name']]

    def get_func(self, vpn_name, kerberos_realm_name):
        # GET /msgVpns/{msgVpnName}/authenticationKerberosRealms/{kerberosRealmName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'authenticationKerberosRealms', kerberos_realm_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, kerberos_realm_name, settings=None):
        # POST /msgVpns/{msgVpnName}/authenticationKerberosRealms
        data = {
            'msgVpnName': vpn_name,
            self.OBJECT_KEY: kerberos_realm_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG,
                      'msgVpns', vpn_name, 'authenticationKerberosRealms']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def update_func(self, vpn_name, kerberos_realm_name, settings=None, delta_settings=None):
        # PATCH /msgVpns/{msgVpnName}/authenticationKerberosRealms/{kerberosRealmName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'authenticationKerberosRealms', kerberos_realm_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def delete_func(self, vpn_name, kerberos_realm_name):
        # DELETE /msgVpns/{msgVpnName}/authenticationKerberosRealms/{kerberosRealmName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns',
                      vpn_name, 'authenticationKerberosRealms', kerberos_realm_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['kerberos_realm', 'kerberos_realm_name'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceAuthenticationKerberosRealmTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
