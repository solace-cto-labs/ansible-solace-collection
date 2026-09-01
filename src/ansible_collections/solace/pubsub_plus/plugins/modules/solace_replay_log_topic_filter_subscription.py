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
module: solace_replay_log_topic_filter_subscription
short_description: topic filter subscription on a replay log
description:
- "Configure a Topic Filter Subscription object on a Replay Log. Allows addition and removal of Topic Filter Subscription objects on a replay log."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  createMsgVpnReplayLogTopicFilterSubscription"
options:
  name:
    description: The topic filter subscription. Maps to 'topicFilterSubscription' in the API.
    required: true
    type: str
    aliases: [topic, topic_filter_subscription]
  replay_log_name:
    description: The name of the Replay Log. Maps to 'replayLogName' in the API.
    required: true
    type: str
    aliases: [replay_log]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace.pubsub_plus.solace_replay_log
- module: solace.pubsub_plus.solace_replay_log_topic_filter_subscriptions
- module: solace.pubsub_plus.solace_get_replay_log_topic_filter_subscriptions
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
  solace_replay_log_topic_filter_subscription:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
- name: add subscription
  solace_replay_log_topic_filter_subscription:
    replay_log_name: my-replay-log
    topic: "foo/bar"
    state: present

- name: remove subscription
  solace_replay_log_topic_filter_subscription:
    replay_log_name: my-replay-log
    topic: "foo/bar"
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


class SolaceReplayLogTopicFilterSubscriptionTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'topicFilterSubscription'

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
        return [params['msg_vpn'], params['replay_log_name'], params['name']]

    def get_func(self, vpn_name, replay_log_name, topic_filter_subscription):
        # GET /msgVpns/{msgVpnName}/replayLogs/{replayLogName}/topicFilterSubscriptions/{topicFilterSubscription}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'replayLogs', replay_log_name, 'topicFilterSubscriptions', topic_filter_subscription]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, replay_log_name, topic_filter_subscription, settings=None):
        # POST /msgVpns/{msgVpnName}/replayLogs/{replayLogName}/topicFilterSubscriptions
        data = {
            self.OBJECT_KEY: topic_filter_subscription
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'replayLogs', replay_log_name, 'topicFilterSubscriptions']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, replay_log_name, topic_filter_subscription):
        # DELETE /msgVpns/{msgVpnName}/replayLogs/{replayLogName}/topicFilterSubscriptions/{topicFilterSubscription}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'replayLogs', replay_log_name, 'topicFilterSubscriptions', topic_filter_subscription]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['topic', 'topic_filter_subscription']),
        replay_log_name=dict(type='str', required=True, aliases=['replay_log'])
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceReplayLogTopicFilterSubscriptionTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
