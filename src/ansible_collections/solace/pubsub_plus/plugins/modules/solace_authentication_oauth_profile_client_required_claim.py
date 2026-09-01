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
module: solace_authentication_oauth_profile_client_required_claim
short_description: client required claim for an oauth profile
description:
- "Configure a Client Required Claim object on an Authentication OAuth Profile. Allows addition, removal and configuration of objects in an idempotent manner."
notes:
- "Module Sempv2 Config: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/\
  createMsgVpnAuthenticationOauthProfileClientRequiredClaim"
options:
  name:
    description: The name of the Client Required Claim. Maps to 'clientRequiredClaimName' in the API.
    required: true
    type: str
    aliases: [client_required_claim_name]
  oauth_profile_name:
    description: The name of the OAuth Profile. Maps to 'oauthProfileName' in the API.
    required: true
    type: str
extends_documentation_fragment:
- solace.pubsub_plus.solace.broker
- solace.pubsub_plus.solace.vpn
- solace.pubsub_plus.solace.sempv2_settings
- solace.pubsub_plus.solace.state
seealso:
- module: solace.pubsub_plus.solace_authentication_oauth_profile
- module: solace.pubsub_plus.solace_get_authentication_oauth_profile_client_required_claims
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
  solace_authentication_oauth_profile_client_required_claim:
    host: "{{ sempv2_host }}"
    port: "{{ sempv2_port }}"
    secure_connection: "{{ sempv2_is_secure_connection }}"
    username: "{{ sempv2_username }}"
    password: "{{ sempv2_password }}"
    timeout: "{{ sempv2_timeout }}"
    msg_vpn: "{{ vpn }}"
tasks:
- name: add
  solace_authentication_oauth_profile_client_required_claim:
    name: my-claim
    oauth_profile_name: my-profile
    settings:
      clientRequiredClaimValue: my-value
    state: present

- name: remove
  solace_authentication_oauth_profile_client_required_claim:
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


class SolaceAuthenticationOAuthProfileClientRequiredClaimTask(SolaceBrokerCRUDTask):

    OBJECT_KEY = 'clientRequiredClaimName'

    def __init__(self, module):
        super().__init__(module)
        self.sempv2_api = SolaceSempV2Api(module)

    def get_args(self):
        params = self.get_module().params
        return [params['msg_vpn'], params['oauth_profile_name'], params['name']]

    def get_func(self, vpn_name, oauth_profile_name, client_required_claim_name):
        # GET /msgVpns/{msgVpnName}/authenticationOauthProfiles/{oauthProfileName}/clientRequiredClaims/{clientRequiredClaimName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'authenticationOauthProfiles',
                      oauth_profile_name, 'clientRequiredClaims', client_required_claim_name]
        return self.sempv2_api.get_object_settings(self.get_config(), path_array)

    def create_func(self, vpn_name, oauth_profile_name, client_required_claim_name, settings=None):
        # POST /msgVpns/{msgVpnName}/authenticationOauthProfiles/{oauthProfileName}/clientRequiredClaims
        data = {
            'msgVpnName': vpn_name,
            'oauthProfileName': oauth_profile_name,
            self.OBJECT_KEY: client_required_claim_name
        }
        data.update(settings if settings else {})
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name,
                      'authenticationOauthProfiles', oauth_profile_name, 'clientRequiredClaims']
        return self.sempv2_api.make_post_request(self.get_config(), path_array, data)

    def update_func(self, vpn_name, oauth_profile_name, client_required_claim_name, settings=None, delta_settings=None):
        # PATCH /msgVpns/{msgVpnName}/authenticationOauthProfiles/{oauthProfileName}/clientRequiredClaims/{clientRequiredClaimName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'authenticationOauthProfiles',
                      oauth_profile_name, 'clientRequiredClaims', client_required_claim_name]
        return self.sempv2_api.make_patch_request(self.get_config(), path_array, settings)

    def delete_func(self, vpn_name, oauth_profile_name, client_required_claim_name):
        # DELETE /msgVpns/{msgVpnName}/authenticationOauthProfiles/{oauthProfileName}/clientRequiredClaims/{clientRequiredClaimName}
        path_array = [SolaceSempV2Api.API_BASE_SEMPV2_CONFIG, 'msgVpns', vpn_name, 'authenticationOauthProfiles',
                      oauth_profile_name, 'clientRequiredClaims', client_required_claim_name]
        return self.sempv2_api.make_delete_request(self.get_config(), path_array)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['client_required_claim_name']),
        oauth_profile_name=dict(type='str', required=True)
    )
    arg_spec = SolaceTaskBrokerConfig.arg_spec_broker_config()
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_vpn())
    arg_spec.update(SolaceTaskBrokerConfig.arg_spec_crud())
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )
    solace_task = SolaceAuthenticationOAuthProfileClientRequiredClaimTask(module)
    solace_task.execute()


def main():
    run_module()


if __name__ == '__main__':
    main()
