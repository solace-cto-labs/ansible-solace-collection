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
module: solace_telemetry_profile_acl_connect_exceptions
short_description: list of acl connect exceptions on a telemetry profile
description:
- "Configure a list of ACL Connect Exception objects on a Telemetry Profile in a single transaction."
- "Allows addition and removal of a list of ACL Connect Exception objects as well as replacement of all existing objects on a telemetry profile."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates the object list."
- "To delete all objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  createMsgVpnTelemetryProfileAclConnectException"
options:
  names:
    description: The IP address/netmask of the connect exception. Maps to 'receiverAclConnectExceptionAddress' in the SEMP v2 API.
    required: true
    type: list
    aliases: [addresses, acl_connect_exception_addresses]
    elements: str
  telemetry_profile_name:
    description: The name of the Telemetry Profile. Maps to 'telemetryProfileName' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace.pubsub_plus.solace_telemetry_profile
- module: solace.pubsub_plus.solace_telemetry_profile_acl_connect_exception
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
    solace_telemetry_profile_acl_connect_exceptions:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
  tasks:
  - name: add list
    solace_telemetry_profile_acl_connect_exceptions:
      telemetry_profile_name: my-profile
      addresses:
        - "192.168.1.0/24"
        - "10.0.0.0/8"
      state: present

  - name: replace list
    solace_telemetry_profile_acl_connect_exceptions:
      telemetry_profile_name: my-profile
      addresses:
        - "172.16.0.0/12"
      state: exactly

  - name: delete all
    solace_telemetry_profile_acl_connect_exceptions:
      telemetry_profile_name: my-profile
      addresses: null
      state: exactly
'''

RETURN = '''
response:
    description: The response of the operation.
    type: dict
    returned: always
    sample:
      success:
        response:
          -   added: "192.168.1.0/24"
          -   deleted: "10.0.0.0/8"
      error:
        response:
          -   error: "invalid-address"
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDListTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceTelemetryProfileAclConnectExceptionsTask(SolaceBrokerCRUDListTask):

    OBJECT_KEY = 'receiverAclConnectExceptionAddress'

    def __init__(self, module):
        super().__init__(module)

    def get_objects_path_array(self) -> list:
        # GET /msgVpns/{msgVpnName}/telemetryProfiles/{telemetryProfileName}/receiverAclConnectExceptions
        params = self.get_config().get_params()
        return ['msgVpns', params['msg_vpn'], 'telemetryProfiles', params['telemetry_profile_name'], 'receiverAclConnectExceptions']

    def get_objects_result_data_object_key(self) -> str:
        return self.OBJECT_KEY

    def get_crud_args(self, object_key) -> list:
        params = self.get_module().params
        return [params['msg_vpn'], params['telemetry_profile_name'], object_key]

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
        telemetry_profile_name=dict(type='str', required=True),
        names=dict(type='list',
                   required=True,
                   aliases=['addresses', 'acl_connect_exception_addresses'],
                   elements='str'
                   ),
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud_list())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceTelemetryProfileAclConnectExceptionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
