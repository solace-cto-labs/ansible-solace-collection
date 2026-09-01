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
module: solace_distributed_cache_cluster_topics
short_description: list of topics on a cache cluster
description:
- "Configure a list of Topic objects on a Cache Cluster in a single transaction."
- "Allows addition and removal of a list of Topic objects as well as replacement of all existing objects on a cache cluster."
- "Supports 'transactional' behavior with rollback to original list in case of error."
- "De-duplicates the Topic object list."
- "To delete all Topic objects, use state='exactly' with an empty/null list (see examples)."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  createMsgVpnDistributedCacheClusterTopic"
options:
  names:
    description: The topics. Maps to 'topic' in the SEMP v2 API.
    required: true
    type: list
    aliases: [topics]
    elements: str
  cluster_name:
    description: The name of the Cache Cluster. Maps to 'clusterName' in the API.
    required: true
    type: str
  cache_name:
    description: The name of the Distributed Cache. Maps to 'cacheName' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state_crud_list
seealso:
- module: solace.pubsub_plus.solace_distributed_cache_cluster
- module: solace.pubsub_plus.solace_distributed_cache_cluster_topic
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
    solace_distributed_cache_cluster_topics:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
  tasks:
  - name: add list of topics
    solace_distributed_cache_cluster_topics:
      cache_name: my-cache
      cluster_name: my-cluster
      topics:
        - "foo/>"
        - "bar/>"
      state: present

  - name: replace topics
    solace_distributed_cache_cluster_topics:
      cache_name: my-cache
      cluster_name: my-cluster
      topics:
        - "baz/>"
      state: exactly

  - name: delete all topics
    solace_distributed_cache_cluster_topics:
      cache_name: my-cache
      cluster_name: my-cluster
      topics: null
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
          -   added: "foo/>"
          -   deleted: "bar/>"
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDListTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceDistributedCacheClusterTopicsTask(SolaceBrokerCRUDListTask):

    OBJECT_KEY = 'topic'

    def __init__(self, module):
        super().__init__(module)

    def get_objects_path_array(self) -> list:
        # GET .../clusters/{clusterName}/topics
        params = self.get_config().get_params()
        return ['msgVpns', params['msg_vpn'], 'distributedCaches', params['cache_name'],
                'clusters', params['cluster_name'], 'topics']

    def get_objects_result_data_object_key(self) -> str:
        return self.OBJECT_KEY

    def get_crud_args(self, object_key) -> list:
        params = self.get_module().params
        return [params['msg_vpn'], params['cache_name'], params['cluster_name'], object_key]

    def create_func(self, vpn_name, cache_name, cluster_name, topic, settings=None):
        # POST .../clusters/{clusterName}/topics
        data = {
            'msgVpnName': vpn_name,
            'cacheName': cache_name,
            'clusterName': cluster_name,
            self.OBJECT_KEY: topic
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'distributedCaches', cache_name,
                      'clusters', cluster_name, 'topics']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def delete_func(self, vpn_name, cache_name, cluster_name, topic):
        # DELETE .../clusters/{clusterName}/topics/{topic}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'distributedCaches', cache_name,
                      'clusters', cluster_name, 'topics', topic]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        cluster_name=dict(type='str', required=True),
        cache_name=dict(type='str', required=True),
        names=dict(type='list',
                   required=True,
                   aliases=['topics'],
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

    solace_task = SolaceDistributedCacheClusterTopicsTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
