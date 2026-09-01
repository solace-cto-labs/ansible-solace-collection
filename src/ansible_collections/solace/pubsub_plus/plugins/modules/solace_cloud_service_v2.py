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
module: solace_cloud_service_v2
short_description: manage Solace Cloud services (v2 API)
description:
- "Create & delete Solace PubSub+ Cloud event broker services using the Mission Control v2 REST API."
- "Uses async 'operations' to track long running create/delete requests."
- "Note: updating an existing service in place is not supported by the API; delete and re-create instead."
notes:
- "Reference: https://api.solace.dev/cloud/reference/using-the-v2-rest-apis-for-pubsub-cloud"
- "Module Sempv2 Config: https://api.solace.cloud/api/v2/missionControl/eventBrokerServices"
options:
  name:
    description: The name of the service. Maps to 'name' in the API. Mandatory for state='present'.
    required: false
    type: str
  solace_cloud_service_id:
    description:
    - The service id of a service in Solace Cloud.
    - Allowed option for state='absent'.
    type: str
    required: false
    aliases: [service_id]
  wait_timeout_minutes:
    description:
    - Minutes to wait for the async create/delete operation to complete. Module polls the operation every 30 seconds.
    - wait_timeout_minutes == 0 ==> no waiting, module returns immediately.
    type: int
    required: false
    default: 30
  solace_cloud_settings:
    description:
    - Additional settings for state=present. See the v2 API reference for the eventBrokerServices create body.
    - "Note: For state=present, provide at least: serviceClassId, datacenterId, eventBrokerVersion."
    type: dict
    required: false
    aliases: [settings]
extends_documentation_fragment:
- solace.pubsub_plus.solace.solace_cloud_config_solace_cloud
- solace.pubsub_plus.solace.state
seealso:
- module: solace.pubsub_plus.solace_cloud_service
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
- name: create service
  solace_cloud_service_v2:
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN }}"
    name: my-service
    settings:
      serviceClassId: enterprise-250-nano
      datacenterId: aws-ca-central-1a
      eventBrokerVersion: "10.10"
    state: present
  register: result

- name: delete service
  solace_cloud_service_v2:
    solace_cloud_api_token: "{{ SOLACE_CLOUD_API_TOKEN }}"
    solace_cloud_service_id: "{{ result.response.id }}"
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError, SolaceError
from ansible.module_utils.basic import AnsibleModule


class SolaceCloudServiceV2Task(SolaceCloudCRUDTask):

    KEY_ID = 'id'
    KEY_NAME = 'name'

    def __init__(self, module):
        super().__init__(module)
        self.solace_cloud_api = SolaceCloudApiV2(module)
        self._service_id = None

    def validate_params(self):
        params = self.get_module().params
        name = params.get('name', None)
        service_id = params.get(self.get_config().PARAM_SERVICE_ID, None)
        state = params['state']
        if state == 'present' and not name:
            raise SolaceParamsValidationError(
                'name', name, "required for state='present'")
        if state == 'absent' and not name and not service_id:
            raise SolaceParamsValidationError(
                f"name, {self.get_config().PARAM_SERVICE_ID}", name,
                "at least one is required for state='absent'")

    def get_args(self):
        params = self.get_module().params
        service_id = params.get(self.get_config().PARAM_SERVICE_ID, None)
        if service_id:
            return [self.KEY_ID, service_id]
        return [self.KEY_NAME, params['name']]

    def get_func(self, key, value):
        if key == self.KEY_NAME:
            service = self.solace_cloud_api.find_service_by_name(
                self.get_config(), value)
            if not service:
                return None
            self._service_id = service.get(self.KEY_ID)
        else:
            self._service_id = value
        return self.solace_cloud_api.get_event_broker_service(
            self.get_config(), self._service_id)

    def create_func(self, key, name, settings=None):
        if not settings:
            raise SolaceParamsValidationError(
                'settings', settings, "required for creating a service")
        data = {self.KEY_NAME: name}
        data.update(settings)
        wait = self.get_module().params['wait_timeout_minutes']
        return self.solace_cloud_api.create_service(self.get_config(), data, wait)

    def update_func(self, key, value, settings=None, delta_settings=None):
        msg = [
            f"Solace Cloud Service '{key}={value}' already exists.",
            "Updating an existing service in place is not supported by the API - delete & re-create.",
            "changes requested: see 'delta'"
        ]
        raise SolaceError(msg, dict(delta=delta_settings))

    def delete_func(self, key, value):
        service_id = self._service_id if self._service_id else value
        wait = self.get_module().params['wait_timeout_minutes']
        return self.solace_cloud_api.delete_service(self.get_config(), service_id, wait)


def run_module():
    module_args = dict(
        name=dict(type='str', required=False, default=None),
        wait_timeout_minutes=dict(type='int', required=False, default=30)
    )
    arg_spec = SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud()
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_service_id())
    arg_spec.update(SolaceTaskSolaceCloudServiceConfig.arg_spec_state())
    arg_spec.update(
        SolaceTaskSolaceCloudServiceConfig.arg_spec_solace_cloud_settings())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceCloudServiceV2Task(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
