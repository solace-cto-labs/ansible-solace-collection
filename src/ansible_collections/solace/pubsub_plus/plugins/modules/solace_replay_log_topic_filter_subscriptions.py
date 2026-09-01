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
module: solace_replay_log_topic_filter_subscriptions
short_description: list of topic filter subscriptions on a replay log
description:
- "Configure a list of Topic Filter Subscription objects on a Replay Log in a single transaction."
- "Allows addition and removal of a list of Topic Filter Subscription objects as well as replacement of all existing objects on a replay log."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates Topic Filter Subscription object list."
- "Reports which topics were added, deleted and omitted (duplicates). In case of an error, reports the invalid object."
- "To delete all Topic Filter Subscription objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  createMsgVpnReplayLogTopicFilterSubscription"
options:
  names:
    description: The topic filter subscription. Maps to 'topicFilterSubscription' in the SEMP v2 API.
    required: true
    type: list
    aliases: [topics, topic_filter_subscriptions]
    elements: str
  replay_log_name:
    description: The name of the Replay Log. Maps to 'replayLogName' in the API.
    required: true
    type: str
    aliases: [replay_log]
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace.pubsub_plus.solace_replay_log
- module: solace.pubsub_plus.solace_replay_log_topic_filter_subscription
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
    solace_replay_log_topic_filter_subscriptions:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
  tasks:
  - name: add list of subscriptions
    solace_replay_log_topic_filter_subscriptions:
      replay_log_name: my-replay-log
      topic_filter_subscriptions:
        - topic-1
        - topic-2
      state: present

  - name: replace subscriptions
    solace_replay_log_topic_filter_subscriptions:
      replay_log_name: my-replay-log
      topic_filter_subscriptions:
        - new-topic-1
        - new-topic-2
      state: exactly

  - name: delete all subscriptions
    solace_replay_log_topic_filter_subscriptions:
      replay_log_name: my-replay-log
      topic_filter_subscriptions: null
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
          -   added: topic-1
          -   deleted: topic-2
          -   duplicate: duplicate-topic
      error:
        response:
          -   error: /invalid-topic
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


class SolaceReplayLogTopicFilterSubscriptionsTask(SolaceBrokerCRUDListTask):

    OBJECT_KEY = 'topicFilterSubscription'

    def __init__(self, module):
        super().__init__(module)

    def get_objects_path_array(self) -> list:
        # GET /msgVpns/{msgVpnName}/replayLogs/{replayLogName}/topicFilterSubscriptions
        params = self.get_config().get_params()
        return ['msgVpns', params['msg_vpn'], 'replayLogs', params['replay_log_name'], 'topicFilterSubscriptions']

    def get_objects_result_data_object_key(self) -> str:
        return self.OBJECT_KEY

    def get_crud_args(self, object_key) -> list:
        params = self.get_module().params
        return [params['msg_vpn'], params['replay_log_name'], object_key]

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
        replay_log_name=dict(type='str', required=True, aliases=['replay_log']),
        names=dict(type='list',
                   required=True,
                   aliases=['topics', 'topic_filter_subscriptions'],
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

    solace_task = SolaceReplayLogTopicFilterSubscriptionsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
