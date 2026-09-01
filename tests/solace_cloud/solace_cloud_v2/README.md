# Solace Cloud v2 module tests

Tests for the Solace PubSub+ Cloud **v2** (Mission Control REST API) modules against an
**existing** event broker service:

- `solace_cloud_service_v2` (read / idempotency no-op only; does not provision)
- `solace_cloud_client_profile_v2`
- `solace_cloud_service_hostname_v2`
- `solace_cloud_service_hostnames_v2`

## No secrets in the repo

The API token and account-specific ids are **read from environment variables at runtime**
(via `lookup('env', ...)`). Nothing sensitive is committed or passed on the command line.

| Env var | Required | Purpose |
|---|---|---|
| `SOLACE_CLOUD_API_TOKEN` | yes | Solace Cloud API (Bearer) token |
| `SOLACE_CLOUD_SERVICE_ID` | yes | id of an existing event broker service |
| `SOLACE_CLOUD_CONNECTION_ENDPOINT_ID` | for hostnames test | connection endpoint id on the service |
| `SOLACE_CLOUD_HOME` | no (default `us`) | region: `us` / `au` / `eu` / `sg` |
| `SOLACE_CLOUD_SERVICE_NAME` | no | enables the `service_v2` read test |
| `SOLACE_CLOUD_TEST_HOSTNAME` | no | hostname to add (default `pgtestch1.messaging.solace.cloud`) |

## Run

```bash
export SOLACE_CLOUD_API_TOKEN='...'          # do NOT commit this
export SOLACE_CLOUD_SERVICE_ID='...'
export SOLACE_CLOUD_CONNECTION_ENDPOINT_ID='...'   # optional (hostnames test)
export SOLACE_CLOUD_SERVICE_NAME='...'             # optional (service read test)
export ANSIBLE_COLLECTIONS_PATH="$PWD/src"         # if running from a source checkout

./_run.sh
```

Notes:
- The hostname default uses a Solace-managed `*.messaging.solace.cloud` name (no custom
  certificate required). Adding a custom-domain FQDN requires a custom server certificate
  installed on the service first.
- `service_v2` create/delete (provisioning) is intentionally **not** exercised here - it is
  billable and slow. The read test only confirms an existing service is found with no change.
- Rotate any API token used for testing when finished.
