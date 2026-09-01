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
module: solace_telemetry_profile_trace_filter_subscriptions
short_description: list of subscriptions on a telemetry profile trace filter
description:
- "Configure a list of Subscription objects on a Telemetry Profile Trace Filter in a single transaction."
- "Allows addition and removal of a list of Subscription objects as well as replacement of all existing objects on a trace filter."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates the Subscription object list."
- "To delete all Subscription objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  createMsgVpnTelemetryProfileTraceFilterSubscription"
options:
  names:
    description: The subscription topics. Maps to 'subscription' in the SEMP v2 API.
    required: true
    type: list
    aliases: [topics, subscriptions]
    elements: str
  subscription_syntax:
    description: The syntax of the subscription topics. Maps to 'subscriptionSyntax' in the API.
    required: false
    default: smf
    type: str
    choices: [smf, mqtt]
  trace_filter_name:
    description: The name of the Trace Filter. Maps to 'traceFilterName' in the API.
    required: true
    type: str
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
- module: solace.pubsub_plus.solace_telemetry_profile_trace_filter
- module: solace.pubsub_plus.solace_telemetry_profile_trace_filter_subscription
- module: solace.pubsub_plus.solace_get_telemetry_profile_trace_filter_subscriptions
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
    solace_telemetry_profile_trace_filter_subscriptions:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
  tasks:
  - name: add list of subscriptions
    solace_telemetry_profile_trace_filter_subscriptions:
      telemetry_profile_name: my-profile
      trace_filter_name: my-filter
      subscription_syntax: smf
      subscriptions:
        - "topic-1/>"
        - "topic-2/>"
      state: present

  - name: replace subscriptions
    solace_telemetry_profile_trace_filter_subscriptions:
      telemetry_profile_name: my-profile
      trace_filter_name: my-filter
      subscriptions:
        - "new-topic/>"
      state: exactly

  - name: delete all subscriptions
    solace_telemetry_profile_trace_filter_subscriptions:
      telemetry_profile_name: my-profile
      trace_filter_name: my-filter
      subscriptions: null
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
          -   added: "topic-1/>"
          -   deleted: "topic-2/>"
      error:
        response:
          -   error: "invalid-topic"
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api, SolaceApiError
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_consts import SolaceTaskOps
from ansible.module_utils.basic import AnsibleModule


class SolaceTelemetryProfileTraceFilterSubscriptionsTask(SolaceBrokerCRUDTask):

    # a subscription is identified by the composite (subscription, subscriptionSyntax);
    # the URI key order is '{subscription},{subscriptionSyntax}'
    OBJECT_KEY = 'subscription'
    SYNTAX_KEY = 'subscriptionSyntax'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def _collection_path_array(self) -> list:
        p = self.get_module().params
        return [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', p['msg_vpn'], 'telemetryProfiles',
                p['telemetry_profile_name'], 'traceFilters', p['trace_filter_name'], 'subscriptions']

    def get_existing(self) -> set:
        try:
            data = self.sempv2_api.make_get_request(
                self.get_config(), self._collection_path_array(), SolaceTaskOps.OP_READ_OBJECT_LIST)
        except SolaceApiError as e:
            if e.get_resp()['status_code'] == 404:
                return set()
            raise
        return set((d.get(self.OBJECT_KEY), d.get(self.SYNTAX_KEY))
                   for d in (data or []) if isinstance(d, dict))

    def create_one(self, subscription, subscription_syntax):
        p = self.get_module().params
        data = {
            'msgVpnName': p['msg_vpn'],
            'telemetryProfileName': p['telemetry_profile_name'],
            'traceFilterName': p['trace_filter_name'],
            self.OBJECT_KEY: subscription,
            self.SYNTAX_KEY: subscription_syntax
        }
        return self.sempv2_api.make_post_request(self.get_config(), self._collection_path_array(), data)

    def delete_one(self, subscription, subscription_syntax):
        sub_uri = ','.join([subscription, subscription_syntax])
        return self.sempv2_api.make_delete_request(
            self.get_config(), self._collection_path_array() + [sub_uri])

    def do_task(self):
        self.validate_params()
        p = self.get_module().params
        state = p['state']
        syntax = p['subscription_syntax']
        is_check_mode = self.get_module().check_mode
        # dedupe target, preserve order; each name uses the single subscription_syntax
        target = []
        for n in (p['names'] or []):
            if (n, syntax) not in target:
                target.append((n, syntax))
        existing = self.get_existing()
        added = []
        deleted = []
        if state in ('present', 'exactly'):
            for (sub, syn) in target:
                if (sub, syn) not in existing:
                    if not is_check_mode:
                        self.create_one(sub, syn)
                    added.append(sub)
        elif state == 'absent':
            for (sub, syn) in target:
                if (sub, syn) in existing:
                    if not is_check_mode:
                        self.delete_one(sub, syn)
                    deleted.append(sub)
        if state == 'exactly':
            target_set = set(target)
            for (sub, syn) in existing:
                if (sub, syn) not in target_set:
                    if not is_check_mode:
                        self.delete_one(sub, syn)
                    deleted.append(sub)
        changed = bool(added or deleted)
        result = self.create_result(rc=0, changed=changed)
        result['response'] = [{'added': a} for a in added] + [{'deleted': d} for d in deleted]
        return None, result


def run_module():
    module_args = dict(
        telemetry_profile_name=dict(type='str', required=True),
        trace_filter_name=dict(type='str', required=True),
        subscription_syntax=dict(type='str', default='smf', choices=['smf', 'mqtt']),
        names=dict(type='list',
                   required=True,
                   aliases=['topics', 'subscriptions'],
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

    solace_task = SolaceTelemetryProfileTraceFilterSubscriptionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
