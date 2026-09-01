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
module: solace_oauth_profile_resource_server_required_claim
short_description: resource server required claim on a broker oauth profile
description:
- "Allows addition, removal and configuration of Resource Server Required Claim Objects on a broker OAuth Profile in an idempotent manner."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/oauthProfile/\
  createOauthProfileResourceServerRequiredClaim"
options:
  name:
    description: The name of the Resource Server Required Claim. Maps to 'resourceServerRequiredClaimName' in the API.
    required: true
    type: str
    aliases: [resource_server_required_claim_name]
  oauth_profile_name:
    description: The name of the OAuth Profile. Maps to 'oauthProfileName' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace.pubsub_plus.solace_oauth_profile
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
  solace_oauth_profile_resource_server_required_claim:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
tasks:
- name: add
  solace_oauth_profile_resource_server_required_claim:
    name: my-claim
    oauth_profile_name: my-profile
    settings:
      resourceServerRequiredClaimValue: my-value
    state: present

- name: remove
  solace_oauth_profile_resource_server_required_claim:
    name: my-claim
    oauth_profile_name: my-profile
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
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task import SolaceBrokerCRUDTask
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_api import SolaceSempV2Api
from ansible_collections.solace.pubsub_plus.plugins.module_utils.solace_task_config import SolaceTaskBrokerConfig
from ansible.module_utils.basic import AnsibleModule


class SolaceOauthProfileResourceServerRequiredClaimTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'resourceServerRequiredClaimName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['oauth_profile_name'], params['name']]

    def get_func(self, oauth_profile_name, resource_server_required_claim_name):
        # GET /oauthProfiles/{oauthProfileName}/resourceServerRequiredClaims/{resourceServerRequiredClaimName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'oauthProfiles',
                      oauth_profile_name, 'resourceServerRequiredClaims', resource_server_required_claim_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, oauth_profile_name, resource_server_required_claim_name, settings=None):
        # POST /oauthProfiles/{oauthProfileName}/resourceServerRequiredClaims
        data = {
            'oauthProfileName': oauth_profile_name,
            self.OBJECT_KEY: resource_server_required_claim_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'oauthProfiles',
                      oauth_profile_name, 'resourceServerRequiredClaims']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def update_func(self, oauth_profile_name, resource_server_required_claim_name, settings=None, delta_settings=None):
        # PATCH /oauthProfiles/{oauthProfileName}/resourceServerRequiredClaims/{resourceServerRequiredClaimName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'oauthProfiles',
                      oauth_profile_name, 'resourceServerRequiredClaims', resource_server_required_claim_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def delete_func(self, oauth_profile_name, resource_server_required_claim_name):
        # DELETE /oauthProfiles/{oauthProfileName}/resourceServerRequiredClaims/{resourceServerRequiredClaimName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'oauthProfiles',
                      oauth_profile_name, 'resourceServerRequiredClaims', resource_server_required_claim_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['resource_server_required_claim_name']),
        oauth_profile_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    solace_task = SolaceOauthProfileResourceServerRequiredClaimTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
