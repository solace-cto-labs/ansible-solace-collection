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
module: solace_get_telemetry_profile_trace_filter_subscriptions
short_description: get list of subscriptions on a telemetry profile trace filter
description:
- "Get a list of Subscription objects configured on a Telemetry Profile Trace Filter object."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  getMsgVpnTelemetryProfileTraceFilterSubscriptions"
- "Module Sempv2 Monitor: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/msgVpn/\
  getMsgVpnTelemetryProfileTraceFilterSubscriptions"
options:
  telemetry_profile_name:
    description: The name of the Telemetry Profile. Maps to 'telemetryProfileName' in the API.
    required: true
    type: str
  trace_filter_name:
    description: The name of the Trace Filter. Maps to 'traceFilterName' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.get_list
seealso:
- module: solace.pubsub_plus.solace_telemetry_profile_trace_filter_subscription
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
  solace_get_telemetry_profile_trace_filter_subscriptions:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:

- name: get list config
  solace_get_telemetry_profile_trace_filter_subscriptions:
    telemetry_profile_name: my-profile
    trace_filter_name: my-filter
  register: result

- name: print result
  debug:
    msg:
    - "{{ result.result_list }}"
    - "{{ result.result_list_count }}"

- name: get list monitor
  solace_get_telemetry_profile_trace_filter_subscriptions:
    api: monitor
    telemetry_profile_name: my-profile
    trace_filter_name: my-filter
  register: result

- name: print result
  debug:
    msg:
    - "{{ result.result_list }}"
    - "{{ result.result_list_count }}"
'''

RETURN = '''
result_list:
  description: The list of objects found containing requested fields. Payload depends on API called.
  returned: success
  type: list
  elements: dict
result_list_count:
  description: Number of items in result_list.
  returned: success
  type: int
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerGetPagingTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceGetTelemetryProfileTraceFilterSubscriptionsTask(SolaceBrokerGetPagingTask):

    def __init__(self, module):
        super().__init__(module)

    def is_supports_paging(self):
        return False

    def get_path_array(self, params: dict) -> list:
        # GET /msgVpns/{msgVpnName}/telemetryProfiles/{telemetryProfileName}/traceFilters/{traceFilterName}/subscriptions
        return ['msgVpns', params['msg_vpn'], 'telemetryProfiles', params['telemetry_profile_name'],
                'traceFilters', params['trace_filter_name'], 'subscriptions']


def run_module():
    module_args = dict(
        telemetry_profile_name=dict(type='str', required=True),
        trace_filter_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(
        SolaceTaskBrokerConfig.arg_spec_get_object_list_config_montor())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceGetTelemetryProfileTraceFilterSubscriptionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
