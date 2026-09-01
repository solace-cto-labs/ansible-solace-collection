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
module: solace_telemetry_profile_acl_connect_exception
short_description: acl connect exception on a telemetry profile
description:
- "Allows addition and removal of ACL Connect Exception objects on a Telemetry Profile."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  createMsgVpnTelemetryProfileAclConnectException"
options:
  name:
    description: The IP address/netmask of the connect exception. Maps to 'receiverAclConnectExceptionAddress' in the API.
    required: true
    type: str
    aliases: [address, acl_connect_exception_address]
  telemetry_profile_name:
    description: The name of the Telemetry Profile. Maps to 'telemetryProfileName' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace.pubsub_plus.solace_telemetry_profile
- module: solace.pubsub_plus.solace_telemetry_profile_acl_connect_exceptions
- module: solace.pubsub_plus.solace_get_telemetry_profile_acl_connect_exceptions
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
  solace_telemetry_profile_acl_connect_exception:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
- name: add
  solace_telemetry_profile_acl_connect_exception:
    name: "192.168.1.0/24"
    telemetry_profile_name: my-profile
    state: present

- name: remove
  solace_telemetry_profile_acl_connect_exception:
    name: "192.168.1.0/24"
    telemetry_profile_name: my-profile
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


class SolaceTelemetryProfileAclConnectExceptionTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'receiverAclConnectExceptionAddress'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['telemetry_profile_name'], params['name']]

    def get_func(self, vpn_name, telemetry_profile_name, address):
        # GET /msgVpns/{msgVpnName}/telemetryProfiles/{telemetryProfileName}/receiverAclConnectExceptions/{aclConnectExceptionAddress}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'telemetryProfiles', telemetry_profile_name, 'receiverAclConnectExceptions', address]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, telemetry_profile_name, address, settings=None):
        # POST /msgVpns/{msgVpnName}/telemetryProfiles/{telemetryProfileName}/receiverAclConnectExceptions
        data = {
            'msgVpnName': vpn_name,
            'telemetryProfileName': telemetry_profile_name,
            self.OBJECT_KEY: address
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'telemetryProfiles', telemetry_profile_name, 'receiverAclConnectExceptions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, telemetry_profile_name, address):
        # DELETE /msgVpns/{msgVpnName}/telemetryProfiles/{telemetryProfileName}/receiverAclConnectExceptions/{aclConnectExceptionAddress}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'telemetryProfiles', telemetry_profile_name, 'receiverAclConnectExceptions', address]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['address', 'acl_connect_exception_address']),
        telemetry_profile_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceTelemetryProfileAclConnectExceptionTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
