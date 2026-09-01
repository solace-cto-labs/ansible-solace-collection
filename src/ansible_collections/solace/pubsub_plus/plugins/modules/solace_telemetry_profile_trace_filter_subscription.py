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
module: solace_telemetry_profile_trace_filter_subscription
short_description: subscription on a telemetry profile trace filter
description:
- "Allows addition and removal of Subscription objects on a Telemetry Profile Trace Filter."
- "A Subscription is identified by its subscription and subscriptionSyntax. Both form the object's identifier."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  createMsgVpnTelemetryProfileTraceFilterSubscription"
options:
  name:
    description: The subscription topic. Maps to 'subscription' in the API.
    required: true
    type: str
    aliases: [topic, subscription]
  subscription_syntax:
    description: The syntax of the subscription topic. Maps to 'subscriptionSyntax' in the API.
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
- solace.pubsub_plus.solace.state
seealso:
- module: solace.pubsub_plus.solace_telemetry_profile_trace_filter
- module: solace.pubsub_plus.solace_telemetry_profile_trace_filter_subscriptions
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
  solace_telemetry_profile_trace_filter_subscription:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
- name: add subscription
  solace_telemetry_profile_trace_filter_subscription:
    telemetry_profile_name: my-profile
    trace_filter_name: my-filter
    topic: "foo/bar/>"
    subscription_syntax: smf
    state: present

- name: remove subscription
  solace_telemetry_profile_trace_filter_subscription:
    telemetry_profile_name: my-profile
    trace_filter_name: my-filter
    topic: "foo/bar/>"
    subscription_syntax: smf
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_utils import SolaceUtils
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_error import SolaceParamsValidationError
from ansible.module_utils.basic import AnsibleModule


class SolaceTelemetryProfileTraceFilterSubscriptionTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'subscription'
    SUBSCRIPTION_SYNTAX_KEY = 'subscriptionSyntax'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def validate_params(self):
        topic = self.get_module().params['name']
        if SolaceUtils.doesStringContainAnyWhitespaces(topic):
            raise SolaceParamsValidationError('topic',
                                              topic, "must not contain any whitespace")
        return super().validate_params()

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['telemetry_profile_name'], params['trace_filter_name'],
                params['subscription_syntax'], params['name']]

    def get_func(self, vpn_name, telemetry_profile_name, trace_filter_name, subscription_syntax, subscription):
        # GET .../traceFilters/{traceFilterName}/subscriptions/{subscriptionSyntax},{subscription}
        sub_uri = ','.join([subscription, subscription_syntax])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'telemetryProfiles',
                      telemetry_profile_name, 'traceFilters', trace_filter_name, 'subscriptions', sub_uri]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, telemetry_profile_name, trace_filter_name, subscription_syntax, subscription, settings=None):
        # POST .../traceFilters/{traceFilterName}/subscriptions
        data = {
            'msgVpnName': vpn_name,
            'telemetryProfileName': telemetry_profile_name,
            'traceFilterName': trace_filter_name,
            self.SUBSCRIPTION_SYNTAX_KEY: subscription_syntax,
            self.OBJECT_KEY: subscription
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'telemetryProfiles',
                      telemetry_profile_name, 'traceFilters', trace_filter_name, 'subscriptions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, telemetry_profile_name, trace_filter_name, subscription_syntax, subscription):
        # DELETE .../traceFilters/{traceFilterName}/subscriptions/{subscriptionSyntax},{subscription}
        sub_uri = ','.join([subscription, subscription_syntax])
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'telemetryProfiles',
                      telemetry_profile_name, 'traceFilters', trace_filter_name, 'subscriptions', sub_uri]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['topic', 'subscription']),
        subscription_syntax=dict(type='str', default='smf', choices=['smf', 'mqtt']),
        trace_filter_name=dict(type='str', required=True),
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

    solace_task = SolaceTelemetryProfileTraceFilterSubscriptionTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
