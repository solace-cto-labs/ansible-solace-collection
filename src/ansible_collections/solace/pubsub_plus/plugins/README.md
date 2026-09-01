# Collection Plugins Directory

```
├── doc_fragments
│   ├── __pycache__
│   │   └── solace.cpython-36.pyc
│   ├── old_solace.py
│   └── solace.py
├── module_utils
│   ├── __init__.py
│   ├── solace_api.py
│   ├── solace_error.py
│   ├── solace_facts.py
│   ├── solace_sys.py
│   ├── solace_task.py
│   ├── solace_task_config.py
│   └── solace_utils.py
└── modules
    ├── solace_acl_client_connect_exception.py
    ├── solace_acl_profile.py
    ├── solace_acl_publish_topic_exception.py
    ├── solace_acl_subscribe_share_name_exception.py
    ├── solace_acl_subscribe_topic_exception.py
    ├── solace_authentication_kerberos_realm.py
    ├── solace_authentication_oauth_profile.py
    ├── solace_authentication_oauth_profile_client_required_claim.py
    ├── solace_authentication_oauth_profile_resource_server_required_claim.py
    ├── solace_bridge.py
    ├── solace_bridge_remote_subscription.py
    ├── solace_bridge_remote_vpn.py
    ├── solace_bridge_trusted_cn.py
    ├── solace_cert_authority.py
    ├── solace_cert_matching_rule.py
    ├── solace_cert_matching_rule_attribute_filter.py
    ├── solace_cert_matching_rule_condition.py
    ├── solace_client_profile.py
    ├── solace_client_username.py
    ├── solace_client_username_attribute.py
    ├── solace_cloud_account_gather_facts.py
    ├── solace_cloud_client_profile_v2.py
    ├── solace_cloud_get_facts.py
    ├── solace_cloud_get_service.py
    ├── solace_cloud_get_services.py
    ├── solace_cloud_service.py
    ├── solace_cloud_service_hostname_v2.py
    ├── solace_cloud_service_hostnames_v2.py
    ├── solace_cloud_service_v2.py
    ├── solace_distributed_cache.py
    ├── solace_distributed_cache_cluster.py
    ├── solace_distributed_cache_cluster_global_home.py
    ├── solace_distributed_cache_cluster_global_home_topic_prefix.py
    ├── solace_distributed_cache_cluster_global_home_topic_prefixes.py
    ├── solace_distributed_cache_cluster_instance.py
    ├── solace_distributed_cache_cluster_topic.py
    ├── solace_distributed_cache_cluster_topics.py
    ├── solace_dmr_bridge.py
    ├── solace_dmr_cluster.py
    ├── solace_dmr_cluster_cert_matching_rule.py
    ├── solace_dmr_cluster_cert_matching_rule_attribute_filter.py
    ├── solace_dmr_cluster_cert_matching_rule_condition.py
    ├── solace_dmr_cluster_link.py
    ├── solace_dmr_cluster_link_attribute.py
    ├── solace_dmr_cluster_link_remote_address.py
    ├── solace_dmr_cluster_link_trusted_cn.py
    ├── solace_gather_facts.py
    ├── solace_get_acl_profiles.py
    ├── solace_get_authentication_kerberos_realms.py
    ├── solace_get_authentication_oauth_profile_client_required_claims.py
    ├── solace_get_authentication_oauth_profile_resource_server_required_claims.py
    ├── solace_get_authentication_oauth_profiles.py
    ├── solace_get_available.py
    ├── solace_get_bridge_remote_vpns.py
    ├── solace_get_bridges.py
    ├── solace_get_cert_authorities.py
    ├── solace_get_cert_matching_rule_attribute_filters.py
    ├── solace_get_cert_matching_rule_conditions.py
    ├── solace_get_cert_matching_rules.py
    ├── solace_get_client_profiles.py
    ├── solace_get_client_username_attributes.py
    ├── solace_get_client_usernames.py
    ├── solace_get_dmr_bridges.py
    ├── solace_get_dmr_cluster_cert_matching_rule_attribute_filters.py
    ├── solace_get_dmr_cluster_cert_matching_rule_conditions.py
    ├── solace_get_dmr_cluster_cert_matching_rules.py
    ├── solace_get_dmr_cluster_link_attributes.py
    ├── solace_get_dmr_cluster_link_remote_addresses.py
    ├── solace_get_dmr_cluster_link_trusted_cns.py
    ├── solace_get_dmr_cluster_links.py
    ├── solace_get_dmr_clusters.py
    ├── solace_get_facts.py
    ├── solace_get_kafka_receiver_topic_bindings.py
    ├── solace_get_kafka_receivers.py
    ├── solace_get_kafka_sender_queue_bindings.py
    ├── solace_get_kafka_senders.py
    ├── solace_get_magic_queues.py
    ├── solace_get_mqtt_retain_caches.py
    ├── solace_get_mqtt_session_subscriptions.py
    ├── solace_get_mqtt_sessions.py
    ├── solace_get_proxies.py
    ├── solace_get_queue_subscriptions.py
    ├── solace_get_queues.py
    ├── solace_get_rdp_queue_bindings.py
    ├── solace_get_rdp_rest_consumer_oauth_jwt_claims.py
    ├── solace_get_rdp_rest_consumer_trusted_cns.py
    ├── solace_get_rdp_rest_consumers.py
    ├── solace_get_rdps.py
    ├── solace_get_replay_log_topic_filter_subscriptions.py
    ├── solace_get_replay_logs.py
    ├── solace_get_replicated_topics.py
    ├── solace_get_telemetry_profile_acl_connect_exceptions.py
    ├── solace_get_telemetry_profile_trace_filter_subscriptions.py
    ├── solace_get_telemetry_profile_trace_filters.py
    ├── solace_get_telemetry_profiles.py
    ├── solace_get_topic_endpoint_templates.py
    ├── solace_get_topic_endpoints.py
    ├── solace_get_virtual_hostnames.py
    ├── solace_get_vpn_clients.py
    ├── solace_get_vpn_proxies.py
    ├── solace_get_vpns.py
    ├── solace_kafka_receiver.py
    ├── solace_kafka_receiver_topic_binding.py
    ├── solace_kafka_sender.py
    ├── solace_kafka_sender_queue_binding.py
    ├── solace_mqtt_retain_cache.py
    ├── solace_mqtt_session.py
    ├── solace_mqtt_session_subscription.py
    ├── solace_oauth_profile.py
    ├── solace_oauth_profile_access_group.py
    ├── solace_oauth_profile_access_group_vpn_exception.py
    ├── solace_oauth_profile_client_allowed_host.py
    ├── solace_oauth_profile_client_authz_param.py
    ├── solace_oauth_profile_client_required_claim.py
    ├── solace_oauth_profile_default_vpn_exception.py
    ├── solace_oauth_profile_resource_server_required_claim.py
    ├── solace_proxy.py
    ├── solace_queue.py
    ├── solace_queue_cancel_replay.py
    ├── solace_queue_start_replay.py
    ├── solace_queue_subscription.py
    ├── solace_rdp.py
    ├── solace_rdp_queue_binding.py
    ├── solace_rdp_rest_consumer.py
    ├── solace_rdp_rest_consumer_oauth_jwt_claim.py
    ├── solace_rdp_rest_consumer_trusted_cn.py
    ├── solace_replay_log.py
    ├── solace_replay_log_topic_filter_subscription.py
    ├── solace_replay_log_topic_filter_subscriptions.py
    ├── solace_replay_log_trim_logged_msgs.py
    ├── solace_replicated_topic.py
    ├── solace_replicated_topics.py
    ├── solace_telemetry_profile.py
    ├── solace_telemetry_profile_acl_connect_exception.py
    ├── solace_telemetry_profile_acl_connect_exceptions.py
    ├── solace_telemetry_profile_trace_filter.py
    ├── solace_telemetry_profile_trace_filter_subscription.py
    ├── solace_telemetry_profile_trace_filter_subscriptions.py
    ├── solace_topic_endpoint.py
    ├── solace_topic_endpoint_template.py
    ├── solace_virtual_hostname.py
    ├── solace_vpn.py
    └── solace_vpn_proxy.py
```

---
