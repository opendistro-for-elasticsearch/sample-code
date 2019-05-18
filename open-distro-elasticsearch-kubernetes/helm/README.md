# Opendistro Elasticsearch
This chart installs [Opendistro Kibana](https://opendistro.github.io/for-elasticsearch-docs/docs/kibana/) + [Opendistro Elasticsearch](https://opendistro.github.io/for-elasticsearch-docs/docs/elasticsearch/) with configurable TLS, RBAC, and more.
Due to the uniqueness of different users environments, this chart aims to cater to a number of different use cases and setups.

## TL;DR
```
❯ helm package .
❯ helm install opendistro-es-0.0.1.tgz --name opendistro-es
```

## Installing the Chart
To install the chart with the release name `my-release`:

`❯ helm install --name my-release opendistro-es-0.0.1.tgz`

The command deploys OpenDistro Kibana and Elasticsearch with its associated components (data statefulsets, masters, clients) on the Kubernetes cluster in the default configuration.

## Uninstalling the Chart
To delete/uninstall the chart with the release name `my-release`:
```
❯ helm delete --name opendistro-es
```

## Certs, Secrets, and Configuration
Prior to installation there are a number of secrets that can be defined that will get mounted into the
different elasticsearch/kibana components.

### Kibana

#### Kibana.yml Config
All values defined under `kibana.config` will be converted to yaml and mounted into the config directory.

#### Elasticsearch Specific Secrets
Elasticsearch specific values passed in through the environment including `ELASTICSEARCH_USERNAME`, `ELASTICSEARCH_PASSWORD`,
`COOKIE_PASS`, and optionally a keypass phrase under `KEY_PASSPHRASE`.
```
elasticsearchAccount:
  secret: ""
  keyPassphrase:
    enabled: false
```

#### SSL
Optionally you can define ssl secrets for kibana as well as secrets for interactions between kibana and elasticsearch's rest clients:
```
ssl:
  kibana:
    enabled: true
    existingCertSecret: kibana-certs
  elasticsearch:
    enabled: true
    existingCertSecret: elasticsearch-rest-certs
```
The chart expects the `kibana.existingCertSecret` to have the following values:
```
---
apiVersion: v1
kind: Secret
metadata:
  name: kibana-certs
  namespace: desired_namespace
  labels:
    app: elasticsearch
data:
  kibana-crt.pem: base64value
  kibana-key.pem: base64value
  kibana-root-ca.pem: base64value
```
Similarly for the elasticsearch rest certs:
```
---
apiVersion: v1
kind: Secret
metadata:
  name: elasticsearch-rest-certs
  namespace: desired_namespace
  labels:
    app: elasticsearch
data:
  elk-rest-crt.pem: base64value
  elk-rest-key.pem: base64value
  elk-rest-root-ca.pem: base64value

```

### Elasticsearch

#### SSL
For Elasticsearch you can optionally define ssl secrets for elasticsearch transport, rest, and admin certs:
```
ssl:
  transport:
    enabled: true
    existingCertSecret: elasticsearch-transport-certs
  rest:
    enabled: true
    existingCertSecret: elasticsearch-rest-certs
  admin:
    enabled: true
    existingCertSecret: elasticsearch-admin-certs

```
The transport certs are expected to be formatted in the following way:
```
---
apiVersion: v1
kind: Secret
metadata:
  name: elasticsearch-transport-certs
  namespace: desired_namespace
  labels:
    app: elasticsearch
data:
  elk-transport-crt.pem:
  elk-transport-key.pem:
  elk-transport-root-ca.pem:
```
The admin certs are expected to be formatted in the following way:
```
---
apiVersion: v1
kind: Secret
metadata:
  name: elasticsearch-admin-certs
  namespace: desired_namespace
  labels:
    app: elasticsearch
data:
  admin-crt.pem:
  admin-key.pem:
  admin-root-ca.pem:
```

#### Security Configuration
In an effort to avoid having to `exec` into the pod to configure the various security options see
[here](https://github.com/opendistro-for-elasticsearch/security/tree/master/securityconfig),
you can define secrets that map to each config given that each secret contains the matching file name:
```
securityConfig:
  enabled: true
  path: "/usr/share/elasticsearch/plugins/opendistro_security/securityconfig"
  actionGroupsSecret:
  configSecret:
  internalUsersSecret:
  rolesSecret:
  rolesMappingSecret:
```
Example:
```
❯ cat config.yml
opendistro_security:
  dynamic:
    kibana:
      multitenancy_enabled: true
      server_username: atgdev_opendistro-es-svc
      index: '.kibana'
      do_not_fail_on_forbidden: false
    authc:
      ldap_service_accounts:
        enabled: true
        order: 1
        http_authenticator:
.......
❯ kubectl create secret generic -n logging security-config --from-file=config.yml
```
By coupling the above secrets with `opendistro_security.allow_default_init_securityindex: true` in your
`elasticsearch.config:` at startup all of the secrets will be mounted in and read.

Alternatively you can set `securityConfig.enabled` to `false` and `exec` into the container and make changes as you see fit using the instructions
[here](https://github.com/opendistro-for-elasticsearch/security/blob/master/securityconfig/elasticsearch.yml.example)

#### elasticsearch.yml Config
All values defined under `elasticsearch.config` will be converted to yaml and mounted into the config directory.
See example [here](https://github.com/opendistro-for-elasticsearch/security/blob/master/securityconfig/elasticsearch.yml.example)

#### logging.yml Config
All values defined under `elasticsearch.loggingConfig` will be converted to yaml and mounted into the config directory.

#### log4j2.properties Config
All values defined under `elasticsearch.log4jConfig` will be mounted into the config directory.

### Configuration
The following table lists the configurable parameters of the opendistro elasticsearch chart and their default values.

| Parameter                                                 | Description                                                                                                                                              | Default                                                                 |
|-----------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| `kibana.enabled`                                          | Enable the installation of kibana                                                                                                                        | `true`                                                                  |
| `kibana.image`                                            | Kibana container image                                                                                                                                   | `amazon/opendistro-for-elasticsearch-kibana`                            |
| `kibana.imageTag`                                         | Kibana container image  tag                                                                                                                              | `0.8.0`                                                                 |
| `kibana.replicas`                                         | Number of Kibana instances to deploy                                                                                                                     | `1`                                                                     |
| `kibana.port`                                             | Internal Port for service                                                                                                                                | `5601`                                                                  |
| `kibana.externalPort`                                     | External Port for service                                                                                                                                | `443`                                                                   |
| `kibana.resources`                                        | Kibana pod resource requests & limits                                                                                                                    | `{}`                                                                    |
| `kibana.elasticsearchAccount.secret`                      | The name of the secret with the Kibana server user as configured in your kibana.yml                                                                      | `""`                                                                    |
| `kibana.elasticsearchAccount.keyPassphrase.enabled`       | Enable mounting in keypassphrase for the `elasticsearchAccount`                                                                                          | `false`                                                                 |
| `kibana.ssl.kibana.enabled`                               | Enabled SSL for kibana                                                                                                                                   | `false`                                                                 |
| `kibana.ssl.kibana.existingCertSecret`                    | Name of secret that contains the Kibana certs                                                                                                            | `""`                                                                    |
| `kibana.ssl.elasticsearch.enabled`                        | Enable SSL for interactions between Kibana and Elasticsearch REST clients                                                                                | `false`                                                                 |
| `kibana.ssl.elasticsearch.existingCertSecret`             | Name of secret that contains the Elasticsearch REST certs                                                                                                | `""`                                                                    |
| `kibana.configDirectory`                                  | Location of where to mount in kibana specific configuration                                                                                              | `"/usr/share/kibana/config"`                                            |
| `kibana.certsDirectory`                                   | Location of where to mount in kibana certs configuration                                                                                                 | `"/usr/share/kibana/certs"`                                             |
| `kibana.ingress.enabled`                                  | Enable Kibana Ingress                                                                                                                                    | `false`                                                                 |
| `kibana.ingress.annotations`                              | Kibana Ingress annotations                                                                                                                               | `{}`                                                                    |
| `kibana.ingress.hosts`                                    | Kibana Ingress Hostnames                                                                                                                                 | `[]`                                                                    |
| `kibana.ingress.tls`                                      | Kibana Ingress TLS configuration                                                                                                                         | `[]`                                                                    |
| `kibana.ingress.labels`                                   | Kibana Ingress labels                                                                                                                                    | `{}`                                                                    |
| `kibana.ingress.path`                                     | Kibana Ingress paths                                                                                                                                     | `[]`                                                                    |
| `kibana.config`                                           | Kibana Configuration (`kibana.yml`)                                                                                                                      | `{}`                                                                    |
| `kibana.nodeSelector`                                     | Define which Nodes the Pods are scheduled on.                                                                                                            | `{}`                                                                    |
| `kibana.tolerations`                                      | If specified, the pod's tolerations.                                                                                                                     | `[]`                                                                    |
| `kibana.serviceAccount.create`                            | Create a default serviceaccount for Kibana to use                                                                                                        | `true`                                                                  |
| `kibana.serviceAccount.name`                              | Name for Kibana serviceaccount                                                                                                                           | `""`                                                                    |
| `kibana.extraEnvs`                                        | Extra environments variables to be passed to kibana                                                                                                      | `[]`                                                                    |
| `clusterName`                                             | Name of elasticsearch cluster                                                                                                                            | `"elasticsearch"`                                                       |
| `psp.create`                                              | Create and use `podsecuritypolicy`  resources                                                                                                            | `"true"`                                                                |
| `rbac.enabled`                                            | Create and use `rbac` resources                                                                                                                          | `"true"`                                                                |
| `elasticsearch.securityConfig.enabled`                    | Use custom [security configs](https://github.com/opendistro-for-elasticsearch/security/tree/master/securityconfig)                                       | `"true"`                                                                |
| `elasticsearch.securityConfig.path`                       | Path to security config files                                                                                                                            | `"/usr/share/elasticsearch/plugins/opendistro_security/securityconfig"` |
| `elasticsearch.securityConfig.actionGroupsSecret`         | Name of secret with [action_groups.yml](https://github.com/opendistro-for-elasticsearch/security/blob/master/securityconfig/action_groups.yml) defined   | `""`                                                                    |
| `elasticsearch.securityConfig.configSecret`               | Name of secret with [config.yml](https://github.com/opendistro-for-elasticsearch/security/blob/master/securityconfig/config.yml) defined                 | `""`                                                                    |
| `elasticsearch.securityConfig.internalUsersSecret`        | Name of secret with [internal_users.yml](https://github.com/opendistro-for-elasticsearch/security/blob/master/securityconfig/internal_users.yml) defined | `""`                                                                    |
| `elasticsearch.securityConfig.rolesSecret`                | Name of secret with [roles.yml](https://github.com/opendistro-for-elasticsearch/security/blob/master/securityconfig/roles.yml) defined                   | `""`                                                                    |
| `elasticsearch.securityConfig.rolesMappingSecret`         | Name of secret with [roles_mapping.yml](https://github.com/opendistro-for-elasticsearch/security/blob/master/securityconfig/roles_mapping.yml) defined   | `""`                                                                    |
| `elasticsearch.securityConfig.rolesMappingSecret`         | Name of secret with [roles_mapping.yml](https://github.com/opendistro-for-elasticsearch/security/blob/master/securityconfig/roles_mapping.yml) defined   | `""`                                                                    |
| `elasticsearch.ssl.transport.enabled`                     | Enable Transport SSL for Elasticsearch                                                                                                                   | `false`                                                                 |
| `elasticsearch.ssl.transport.existingCertSecret`          | Name of secret that contains the transport certs                                                                                                         | `""`                                                                    |
| `elasticsearch.ssl.rest.enabled`                          | Enable REST SSL for Elasticsearch                                                                                                                        | `false`                                                                 |
| `elasticsearch.ssl.rest.existingCertSecret`               | Name of secret that contains the Elasticsearch REST certs                                                                                                | `""`                                                                    |
| `elasticsearch.ssl.admin.enabled`                         | Enable Admin SSL cert usage for Elasticsearch                                                                                                            | `false`                                                                 |
| `elasticsearch.ssl.admin.existingCertSecret`              | Name of secret that contains the admin users Elasticsearch certs                                                                                         | `""`                                                                    |
| `elasticsearch.master.replicas`                           | Number of Elasticsearch masters to spin up                                                                                                               | `3`                                                                     |
| `elasticsearch.master.nodeAffinity`                       | Elasticsearch masters nodeAffinity                                                                                                                       | `{}`                                                                    |
| `elasticsearch.master.resources`                          | Elasticsearch masters resource requests & limits                                                                                                         | `{}`                                                                    |
| `elasticsearch.master.javaOpts`                           | Elasticsearch masters configurable java options to pass to startup script                                                                                | `"-Xms512m -Xmx512m"`                                                   |
| `elasticsearch.master.podDisruptionBudget.enabled`        | If true, create a disruption budget for elasticsearch master                                                                                             | `false`                                                                 |
| `elasticsearch.master.podDisruptionBudget.minAvailable`   | Minimum number / percentage of pods that should remain scheduled                                                                                         | `1`                                                                     |
| `elasticsearch.master.podDisruptionBudget.maxUnavailable` | Maximum number / percentage of pods that should remain scheduled                                                                                         | `""`                                                                    |
| `elasticsearch.client.replicas`                           | Number of Elasticsearch clients to spin up                                                                                                               | `3`                                                                     |
| `elasticsearch.client.nodeAffinity`                       | Elasticsearch clients nodeAffinity                                                                                                                       | `{}`                                                                    |
| `elasticsearch.client.resources`                          | Elasticsearch clients resource requests & limits                                                                                                         | `{}`                                                                    |
| `elasticsearch.client.javaOpts`                           | Elasticsearch clients configurable java options to pass to startup script                                                                                | `"-Xms512m -Xmx512m"`                                                   |
| `elasticsearch.client.service.type`                       | Elasticsearch clients service type                                                                                                                       | `ClusterIP`                                                             |
| `elasticsearch.client.service.annotations`                | Elasticsearch clients service annotations                                                                                                                | `{}`                                                                    |
| `elasticsearch.client.ingress.enabled`                    | Enable Elasticsearch clients Ingress                                                                                                                     | `false`                                                                 |
| `elasticsearch.client.ingress.annotations`                | Elasticsearch clients Ingress annotations                                                                                                                | `{}`                                                                    |
| `elasticsearch.client.ingress.hosts`                      | Elasticsearch clients Ingress Hostnames                                                                                                                  | `[]`                                                                    |
| `elasticsearch.client.ingress.tls`                        | Elasticsearch clients Ingress TLS configuration                                                                                                          | `[]`                                                                    |
| `elasticsearch.client.ingress.labels`                     | Elasticsearch clients Ingress labels                                                                                                                     | `{}`                                                                    |
| `elasticsearch.client.podDisruptionBudget.enabled`        | If true, create a disruption budget for elasticsearch client                                                                                             | `false`                                                                 |
| `elasticsearch.client.podDisruptionBudget.minAvailable`   | Minimum number / percentage of pods that should remain scheduled                                                                                         | `1`                                                                     |
| `elasticsearch.client.podDisruptionBudget.maxUnavailable` | Maximum number / percentage of pods that should remain scheduled                                                                                         | `""`                                                                    |
| `elasticsearch.data.replicas`                             | Number of Elasticsearch data nodes to spin up                                                                                                            | `3`                                                                     |
| `elasticsearch.data.nodeAffinity`                         | Elasticsearch data nodeAffinity                                                                                                                          | `{}`                                                                    |
| `elasticsearch.data.resources`                            | Elasticsearch data resource requests & limits                                                                                                            | `{}`                                                                    |
| `elasticsearch.data.javaOpts`                             | Elasticsearch data configurable java options to pass to startup script                                                                                   | `"-Xms512m -Xmx512m"`                                                   |
| `elasticsearch.data.storageClassName`                     | Elasticsearch data storageClassName                                                                                                                      | `"gp2-encrypted"`                                                       |
| `elasticsearch.data.storage`                              | Elasticsearch data storage                                                                                                                               | `"100Gi"`                                                               |
| `elasticsearch.data.podDisruptionBudget.enabled`          | If true, create a disruption budget for elasticsearch data node                                                                                          | `false`                                                                 |
| `elasticsearch.data.podDisruptionBudget.minAvailable`     | Minimum number / percentage of pods that should remain scheduled                                                                                         | `1`                                                                     |
| `elasticsearch.data.podDisruptionBudget.maxUnavailable`   | Maximum number / percentage of pods that should remain scheduled                                                                                         | `""`                                                                    |
| `elasticsearch.config`                                    | Elasticsearch Configuration (`elasticsearch.yml`)                                                                                                        | `{}`                                                                    |
| `elasticsearch.loggingConfig`                             | Elasticsearch Logging Configuration (`logging.yml`)                                                                                                      | see `values.yaml` for defaults                                          |
| `elasticsearch.log4jConfig`                               | Elasticsearch log4j Configuration                                                                                                                        | `""`                                                                    |
| `elasticsearch.transportKeyPassphrase.enabled`            | Elasticsearch transport key passphrase required                                                                                                          | `false`                                                                 |
| `elasticsearch.transportKeyPassphrase.passPhrase`         | Elasticsearch transport key passphrase                                                                                                                   | `""`                                                                    |
| `elasticsearch.sslKeyPassphrase.enabled`                  | Elasticsearch ssl key passphrase required                                                                                                                | `false`                                                                 |
| `elasticsearch.sslKeyPassphrase.passPhrase`               | Elasticsearch ssl key passphrase                                                                                                                         | `""`                                                                    |
| `elasticsearch.image`                                     | Elasticsearch container image                                                                                                                            | `amazon/opendistro-for-elasticsearch`                                   |
| `elasticsearch.imageTag`                                  | Elasticsearch container image  tag                                                                                                                       | `0.8.0`                                                                 |
| `elasticsearch.serviceAccount.create`                     | Create a default serviceaccount for elasticsearch to use                                                                                                 | `true`                                                                  |
| `elasticsearch.serviceAccount.name`                       | Name for elasticsearch serviceaccount                                                                                                                    | `""`                                                                    |
| `elasticsearch.configDirectory`                           | Location of elasticsearch configuration                                                                                                                  | `"/usr/share/elasticsearch/config"`                                     |
| `elasticsearch.maxMapCount`                               | elasticsearch max_map_count                                                                                                                              | `262144`                                                                |
| `elasticsearch.extraEnvs`                                 | Extra environments variables to be passed to elasticsearch services                                                                                      | `[]`                                                                    |


## Acknowledgements
* [Kalvin Chau](https://github.com/kalvinnchau) (Software Engineer - Viasat) for all his help with the Kubernetes internals, certs, and debugging
