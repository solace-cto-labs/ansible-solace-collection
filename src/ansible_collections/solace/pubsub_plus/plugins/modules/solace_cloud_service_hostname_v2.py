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
module: solace_cloud_service_hostname_v2
short_description: dns name (hostname) on a Solace Cloud service (v2 API)
description:
- "Allows addition and removal of DNS Name (hostname) Objects on a connection endpoint of a Solace Cloud event broker service."
- "Uses the Mission Control v2 REST API. An additional hostname is modelled as a 'dnsName' on a connection endpoint of the service."
notes:
- "Reference: https://api.solace.dev/cloud/reference/using-the-v2-rest-apis-for-pubsub-cloud"
- "Module Sempv2 Config: https://api.solace.cloud/api/v2/missionControl/eventBrokerServices/{serviceId}/connectionEndpoints/{connectionEndpointId}/dnsNames"
options:
  name:
    description: The DNS name (hostname). Maps to 'dnsName' in the API.
    required: true
    type: str
    aliases: [hostname, dns_name]
  connection_endpoint_id:
    description: The id of the connection endpoint on the service. Maps to 'connectionEndpointId' in the API.
    required: true
    type: str
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
- module: solace.pubsub_plus.solace_cloud_service_hostname
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
- name: add hostname
  solace_cloud_service_hostname_v2:
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN }}"
    solace_cloud_service_id: "{{ service_id }}"
    connection_endpoint_id: "{{ connection_endpoint_id }}"
    name: "my-broker.example.com"
    state: present

- name: remove hostname
  solace_cloud_service_hostname_v2:
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN }}"
    solace_cloud_service_id: "{{ service_id }}"
    connection_endpoint_id: "{{ connection_endpoint_id }}"
    name: "my-broker.example.com"
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceCloudApiV2, SolaceApiError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskSolaceCloudServiceConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudServiceHostnameV2Task(SolaceCloudCRUDTask):

    OBJECT_KEY = 'dnsName'

    def __init__(self, module):
        super().__init__(module)
        self.solace_cloud_api = SolaceCloudApiV2(module)

    def _wait(self):
        return self.get_module().params['wait_timeout_minutes']

    def _base_path_array(self, name=None):
        api = self.solace_cloud_api
        params = self.get_module().params
        path_array = api.get_mission_control_base_path_array(self.get_config()) + [
            api.API_EVENT_BROKER_SERVICES, params[self.get_config().PARAM_SERVICE_ID],
            api.API_CONNECTION_ENDPOINTS, params['connection_endpoint_id'], api.API_DNS_NAMES]
        if name:
            path_array.append(name)
        return path_array

    def get_args(self):
        return [self.get_module().params['name']]

    def get_func(self, name):
        # the v2 API does not support GET on an individual dnsName (405); list the
        # collection and find it instead.
        try:
            data = self.solace_cloud_api.make_get_request(
                self.get_config(), self._base_path_array(), SolaceTaskOps.OP_READ_OBJECT_LIST)
        except SolaceApiError as e:
            if e.get_resp()['status_code'] == 404:
                return None
            raise
        for d in (data or []):
            if isinstance(d, dict) and (d.get(self.OBJECT_KEY) == name or d.get('name') == name):
                return d
        return None

    def create_func(self, name, settings=None):
        # POST .../connectionEndpoints/{cepId}/dnsNames
        data = {self.OBJECT_KEY: name}
        data.update(settings if settings else {})
        resp = self.solace_cloud_api.make_post_request(
            self.get_config(), self._base_path_array(), data)
        return self.solace_cloud_api._maybe_wait_for_operation(self.get_config(), resp, self._wait(), self.get_module().params[self.get_config().PARAM_SERVICE_ID])

    def delete_func(self, name):
        # DELETE .../connectionEndpoints/{cepId}/dnsNames/{dnsName}
        resp = self.solace_cloud_api.make_delete_request(
            self.get_config(), self._base_path_array(name))
        return self.solace_cloud_api._maybe_wait_for_operation(self.get_config(), resp, self._wait(), self.get_module().params[self.get_config().PARAM_SERVICE_ID])


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['hostname', 'dns_name']),
        connection_endpoint_id=dict(type='str', required=True),
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
    solace_task = SolaceCloudServiceHostnameV2Task(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
