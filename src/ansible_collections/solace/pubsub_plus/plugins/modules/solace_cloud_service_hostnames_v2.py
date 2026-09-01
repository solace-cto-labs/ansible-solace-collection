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
module: solace_cloud_service_hostnames_v2
short_description: list of dns names (hostnames) on a Solace Cloud service (v2 API)
description:
- "Configure a list of DNS Name (hostname) Objects on a connection endpoint of a Solace Cloud event broker service in a single transaction (v2 REST API)."
- "Allows addition and removal of a list of DNS Name objects as well as replacement of all existing objects on the connection endpoint."
- "To delete all DNS Name objects, use state='exactly' with an empty/null list."
notes:
- "Reference: https://api.solace.dev/cloud/reference/using-the-v2-rest-apis-for-pubsub-cloud"
- "Module Sempv2 Config: https://api.solace.cloud/api/v2/missionControl/eventBrokerServices/{serviceId}/connectionEndpoints/{connectionEndpointId}/dnsNames"
options:
  names:
    description: The DNS names (hostnames). Maps to 'dnsName' in the API.
    required: true
    type: list
    elements: str
    aliases: [hostnames, dns_names]
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
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace.pubsub_plus.solace_cloud_service_hostname_v2
- module: solace.pubsub_plus.solace_cloud_service_hostnames
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
- name: set exactly these hostnames
  solace_cloud_service_hostnames_v2:
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN }}"
    solace_cloud_service_id: "{{ service_id }}"
    connection_endpoint_id: "{{ connection_endpoint_id }}"
    names:
      - "broker-1.example.com"
      - "broker-2.example.com"
    state: exactly

- name: delete all hostnames
  solace_cloud_service_hostnames_v2:
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN }}"
    solace_cloud_service_id: "{{ service_id }}"
    connection_endpoint_id: "{{ connection_endpoint_id }}"
    names: null
    state: exactly
'''

RETURN = '''
response:
    description: The list of added/deleted dns names.
    type: dict
    returned: always
    sample:
      success:
        response:
          -   added: "broker-1.example.com"
          -   deleted: "broker-old.example.com"
rc:
    description: Return code. rc=0 on success, rc=1 on error.
    type: int
    returned: always
    sample:
        success:
            rc: 0
        error:
            rc: 1
msg:
    description: The response from the HTTP call in case of error.
    type: dict
    returned: error
'''

from ansible_collections.solace.pubsub_plus.plugins.module_utils import solace_sys  # pylint: disable=unused-import
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceCloudCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceCloudApiV2, SolaceApiError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig, SolaceTaskSolaceCloudServiceConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudServiceHostnamesV2Task(SolaceCloudCRUDTask):

    OBJECT_KEY = 'dnsName'

    def __init__(self, module):
        super().__init__(module)
        self.solace_cloud_api = SolaceCloudApiV2(module)

    def _wait(self):
        return self.get_module().params['wait_timeout_minutes']

    def _collection_path_array(self):
        api = self.solace_cloud_api
        params = self.get_module().params
        return api.get_mission_control_base_path_array(self.get_config()) + [
            api.API_EVENT_BROKER_SERVICES, params[self.get_config().PARAM_SERVICE_ID],
            api.API_CONNECTION_ENDPOINTS, params['connection_endpoint_id'], api.API_DNS_NAMES]

    def get_existing_dns_names(self) -> list:
        module_op = SolaceTaskOps.OP_READ_OBJECT_LIST
        try:
            data = self.solace_cloud_api.make_get_request(
                self.get_config(), self._collection_path_array(), module_op)
        except SolaceApiError as e:
            if e.get_resp()['status_code'] == 404:
                return []
            raise
        names = []
        for d in (data or []):
            if isinstance(d, dict):
                # skip the auto-generated, non-deletable default hostname (the primary
                # 'A' record, e.g. mr-connection-<cepId>...). Only custom (CNAME)
                # hostnames are user-managed, so state=exactly must not try to delete it.
                if d.get('dnsRecordType') == 'A':
                    continue
                n = d.get(self.OBJECT_KEY) or d.get('name')
            else:
                n = d
            if n:
                names.append(n)
        return names

    def create_one(self, name):
        data = {self.OBJECT_KEY: name}
        resp = self.solace_cloud_api.make_post_request(
            self.get_config(), self._collection_path_array(), data)
        return self.solace_cloud_api._maybe_wait_for_operation(self.get_config(), resp, self._wait(), self.get_module().params[self.get_config().PARAM_SERVICE_ID])

    def delete_one(self, name):
        resp = self.solace_cloud_api.make_delete_request(
            self.get_config(), self._collection_path_array() + [name])
        return self.solace_cloud_api._maybe_wait_for_operation(self.get_config(), resp, self._wait(), self.get_module().params[self.get_config().PARAM_SERVICE_ID])

    def do_task(self):
        self.validate_params()
        params = self.get_module().params
        state = params['state']
        is_check_mode = self.get_module().check_mode
        # dedupe target list, preserving order
        target = []
        for n in (params['names'] or []):
            if n not in target:
                target.append(n)
        existing = self.get_existing_dns_names()
        added = []
        deleted = []
        if state in ('present', 'exactly'):
            for n in target:
                if n not in existing:
                    if not is_check_mode:
                        self.create_one(n)
                    added.append(n)
        elif state == 'absent':
            for n in target:
                if n in existing:
                    if not is_check_mode:
                        self.delete_one(n)
                    deleted.append(n)
        if state == 'exactly':
            for n in existing:
                if n not in target:
                    if not is_check_mode:
                        self.delete_one(n)
                    deleted.append(n)
        changed = bool(added or deleted)
        response = [{'added': a} for a in added] + [{'deleted': d} for d in deleted]
        result = self.create_result(rc=0, changed=changed)
        result['response'] = response
        return None, result


def run_module():
    module_args = dict(
        names=dict(type='list', elements='str', required=True,
                   aliases=['hostnames', 'dns_names']),
        connection_endpoint_id=dict(type='str', required=True),
        wait_timeout_minutes=dict(type='int', required=False, default=30)
    )
    arg_spec = SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud()
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_service_id_mandatory())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_state_crud_list())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceCloudServiceHostnamesV2Task(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
