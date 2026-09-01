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
module: solace_cloud_client_profile_v2
short_description: client profile on a Solace Cloud service (v2 API)
description:
- "Allows addition, removal and configuration of Client Profile Objects on a Solace Cloud event broker service using the Mission Control v2 REST API."
notes:
- "Reference: https://api.solace.dev/cloud/reference/using-the-v2-rest-apis-for-pubsub-cloud"
- "Module Sempv2 Config: https://api.solace.cloud/api/v2/missionControl/eventBrokerServices/{serviceId}/clientProfiles"
options:
  name:
    description: The name of the Client Profile. Maps to 'name' in the API.
    required: true
    type: str
    aliases: [client_profile_name]
  wait_timeout_minutes:
    description:
    - Minutes to wait for an async operation to complete (if the API returns one). Polls every 30 seconds.
    - Set to 0 to return immediately.
    type: int
    required: false
    default: 30
extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_config_solace_cloud
- solace.pubsub_plus.solace.solace_cloud_service_config_service_id_mandatory
- solace.pubsub_plus.solace.solace_cloud_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace.pubsub_plus.solace_cloud_service_v2
- module: solace.pubsub_plus.solace_cloud_client_profile
author:
- Paulus Gunadi (@pjgunadi)
'''

EXAMPLES = '''
hosts: all
gather_facts: no
any_errors_fatal: true
collections:
- solace.pubsub_plus
tasks:
- name: add client profile
  solace_cloud_client_profile_v2:
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN }}"
    solace_cloud_service_id: "{{ service_id }}"
    name: my-profile
    settings:
      allowGuaranteedMsgSendEnabled: true
      allowGuaranteedMsgReceiveEnabled: true
    state: present

- name: remove client profile
  solace_cloud_client_profile_v2:
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN }}"
    solace_cloud_service_id: "{{ service_id }}"
    name: my-profile
    state: absent
'''

RETURN = '''
response:
    description: The response from the Solace Cloud v2 request.
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceCloudCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceCloudApiV2
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskSolaceCloudServiceConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudClientProfileV2Task(SolaceCloudCRUDTask):

    OBJECT_KEY = 'name'

    def __init__(self, module):
        super().__init__(module)
        self.solace_cloud_api = SolaceCloudApiV2(module)

    def _service_id(self):
        return self.get_module().params[self.get_config().PARAM_SERVICE_ID]

    def _wait(self):
        return self.get_module().params['wait_timeout_minutes']

    def _base_path_array(self, name=None):
        api = self.solace_cloud_api
        path_array = api.get_mission_control_base_path_array(self.get_config()) + [
            api.API_EVENT_BROKER_SERVICES, self._service_id(), api.API_CLIENT_PROFILES]
        if name:
            path_array.append(name)
        return path_array

    def get_args(self):
        return [self.get_module().params['name']]

    def get_func(self, name):
        # GET .../clientProfiles/{name}
        return self.solace_cloud_api.get_object_settings(self.get_config(), self._base_path_array(name))

    def create_func(self, name, settings=None):
        # POST .../clientProfiles
        data = {self.OBJECT_KEY: name}
        data.update(settings if settings else {})
        resp = self.solace_cloud_api.make_post_request(
            self.get_config(), self._base_path_array(), data)
        return self.solace_cloud_api._maybe_wait_for_operation(self.get_config(), resp, self._wait(), self._service_id())

    def update_func(self, name, settings=None, delta_settings=None):
        # PUT .../clientProfiles/{name}
        data = {self.OBJECT_KEY: name}
        data.update(settings if settings else {})
        resp = self.solace_cloud_api.make_put_request(
            self.get_config(), self._base_path_array(name), data)
        return self.solace_cloud_api._maybe_wait_for_operation(self.get_config(), resp, self._wait(), self._service_id())

    def delete_func(self, name):
        # DELETE .../clientProfiles/{name}
        resp = self.solace_cloud_api.make_delete_request(
            self.get_config(), self._base_path_array(name))
        return self.solace_cloud_api._maybe_wait_for_operation(self.get_config(), resp, self._wait(), self._service_id())


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['client_profile_name']),
        wait_timeout_minutes=dict(type='int', required=False, default=30)
    )
    arg_spec = SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud()
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_service_id_mandatory())
    arg_spec.update(SolaceTaskSolaceCloudServiceConfig.arg_spec_state())
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_settings())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceCloudClientProfileV2Task(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
