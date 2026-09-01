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
module: solace_client_username_attribute
short_description: attribute for a client username
description:
- "Allows addition, removal and configuration of Attribute Objects on a Client Username."
- "An Attribute is a name/value pair. Both the name and the value form the object's identifier - to change a value, remove the old Attribute and add a new one."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  createMsgVpnClientUsernameAttribute"
options:
  name:
    description: The name of the Attribute. Maps to 'attributeName' in the API.
    required: true
    type: str
    aliases: [attribute_name]
  value:
    description: The value of the Attribute. Maps to 'attributeValue' in the API.
    required: true
    type: str
    aliases: [attribute_value]
  client_username:
    description: The name of the Client Username. Maps to 'clientUsername' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace.pubsub_plus.solace_client_username
- module: solace.pubsub_plus.solace_get_client_username_attributes
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
  solace_client_username_attribute:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
  - name: remove
    solace_client_username_attribute:
      name: my-attribute
      value: my-value
      client_username: my-client
      state: absent

  - name: add
    solace_client_username_attribute:
      name: my-attribute
      value: my-value
      client_username: my-client
      state: present
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


class SolaceClientUsernameAttributeTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'attributeName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['client_username'], params['name'], params['value']]

    def get_func(self, vpn_name, client_username, attribute_name, attribute_value):
        # GET /msgVpns/{msgVpnName}/clientUsernames/{clientUsername}/attributes/{attributeName},{attributeValue}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'clientUsernames', client_username, 'attributes', f"{attribute_name},{attribute_value}"]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, client_username, attribute_name, attribute_value, settings=None):
        # POST /msgVpns/{msgVpnName}/clientUsernames/{clientUsername}/attributes
        data = {
            'msgVpnName': vpn_name,
            'clientUsername': client_username,
            self.OBJECT_KEY: attribute_name,
            'attributeValue': attribute_value
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'clientUsernames', client_username, 'attributes']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, client_username, attribute_name, attribute_value):
        # DELETE /msgVpns/{msgVpnName}/clientUsernames/{clientUsername}/attributes/{attributeName},{attributeValue}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'clientUsernames', client_username, 'attributes', f"{attribute_name},{attribute_value}"]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['attribute_name']),
        value=dict(type='str', required=True, aliases=['attribute_value']),
        client_username=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceClientUsernameAttributeTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
