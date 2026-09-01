#!/usr/bin/env bash
# Copyright (c) 2026, Solace Corporation, Paulus Gunadi
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# Runs the Solace Cloud v2 module tests against an EXISTING service.
# All sensitive/account data is taken from the environment (the playbooks read it via
# lookup('env', ...)), so nothing is passed on the command line or stored in the repo.
#
# Required env vars:
#   SOLACE_CLOUD_API_TOKEN               - Solace Cloud API (Bearer) token
#   SOLACE_CLOUD_SERVICE_ID              - id of an existing event broker service
# Optional env vars:
#   SOLACE_CLOUD_CONNECTION_ENDPOINT_ID  - required only for the hostnames test
#   SOLACE_CLOUD_HOME                    - region: us|au|eu|sg (default: us)
#   SOLACE_CLOUD_SERVICE_NAME            - enables the service_v2 read test
#   SOLACE_CLOUD_TEST_HOSTNAME           - hostname to add (default: pgtestch1.messaging.solace.cloud)

scriptDir=$(cd $(dirname "$0") && pwd)
inventory="$scriptDir/localhost.inventory.yml"

if [ -z "$SOLACE_CLOUD_API_TOKEN" ]; then echo ">>> ERROR: missing env var SOLACE_CLOUD_API_TOKEN"; exit 1; fi
if [ -z "$SOLACE_CLOUD_SERVICE_ID" ]; then echo ">>> ERROR: missing env var SOLACE_CLOUD_SERVICE_ID"; exit 1; fi

playbooks=(
  "$scriptDir/service.playbook.yml"
  "$scriptDir/client_profile.playbook.yml"
)
# only run the hostnames test if a connection endpoint id is provided
if [ -n "$SOLACE_CLOUD_CONNECTION_ENDPOINT_ID" ]; then
  playbooks+=("$scriptDir/hostnames.playbook.yml")
else
  echo ">>> NOTE: SOLACE_CLOUD_CONNECTION_ENDPOINT_ID not set - skipping hostnames test"
fi

for playbook in "${playbooks[@]}"; do
  ansible-playbook -i "$inventory" "$playbook"
  code=$?; if [[ $code != 0 ]]; then echo ">>> XT_ERROR - $code - playbook:$playbook"; exit 1; fi
done

echo ">>> SUCCESS: solace_cloud_v2"

###
# The End.
