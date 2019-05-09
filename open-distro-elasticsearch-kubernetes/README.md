# Open Distro for Elasticsearch Deployment for Kubernetes

## Elasticsearch Deployment

### Initial resource creation

With your EKS credentials loaded as part of your `kubeconfig`, you can start the creation of the first few items using the following commands:

```
kubectl apply -f 10-es-namespace.yml
kubectl apply -f 20-es-svc-discovery.yml
kubectl apply -f 20-es-service-account.yml
kubectl apply -f 25-es-sc-gp2.yml
kubectl apply -f 30-es-configmap.yml
kubectl apply -f 35-es-service.yml
```

### Elasticsearch master nodes

Deploy the Elasticsearch master nodes using command:

```
kubectl apply -f 40-es-master-deploy.yml
```

Check for the master node pods to come up using command:

```
kubectl -n elasticsearch get pods
```

If the master nodes are up and running correctly, output would be something like this:

```
NAME                         READY     STATUS    RESTARTS   AGE
es-master-78f97f98d9-275sl   1/1       Running   0          1d
es-master-78f97f98d9-kwqxt   1/1       Running   0          1d
es-master-78f97f98d9-lp6bn   1/1       Running   0          1d
```

You can see whether the master nodes are successfully running by checking the log output of any of these master nodes using the command:

```
kubectl -n elasticsearch logs -f es-master-78f97f98d9-275sl
```

If the log output contains the following message, it means that the Elasticsearch master nodes have clustered successfully:

`[2019-04-04T06:34:16,816][INFO ][o.e.c.s.ClusterApplierService] [es-master-78f97f98d9-275sl] detected_master {es-master-78f97f98d9-kwqxt}`

### Elasticsearch client nodes

Deploy the Elasticsearch client nodes using the command:

```
kubectl apply -f `50-es-client-deploy.yml`
```

Check for the master node pods to come up using the command:

```
kubectl -n elasticsearch get pods
```

If the client nodes are up and running, output would be something like this:

```
NAME                         READY     STATUS    RESTARTS   AGE
es-client-855f48886-75cz8    1/1       Running   0          1d
es-client-855f48886-r4vzn    1/1       Running   0          1d
es-master-78f97f98d9-275sl   1/1       Running   0          1d
es-master-78f97f98d9-kwqxt   1/1       Running   0          1d
es-master-78f97f98d9-lp6bn   1/1       Running   0          1d
```

You can see if the client nodes are successfully running by checking the log output of any of these client nodes using command:

```
kubectl -n elasticsearch logs -f es-master-78f97f98d9-275sl
```

If the log output contains the following message, it means that the Elasticsearch client nodes have clustered successfully:
`[2019-04-04T06:35:57,180][INFO ][o.e.c.s.ClusterApplierService] [es-client-855f48886-75cz8] detected_master {es-master-78f97f98d9-kwqxt}`

### Elasticsearch Data Nodes

Deploy the Elasticsearch data nodes using the command:

```
kubectl apply -f 70-es-data-sts.yml
```

Check for the data node pods to come up using the command:

```
kubectl -n elasticsearch get pods
```

If the data nodes are up and running, output would be something like this :

```
NAME                         READY     STATUS    RESTARTS   AGE
es-client-855f48886-75cz8    1/1       Running   0          1d
es-client-855f48886-r4vzn    1/1       Running   0          1d
es-data-0                    1/1       Running   0          1d
es-data-1                    1/1       Running   0          1d
es-data-2                    1/1       Running   0          1d
es-master-78f97f98d9-275sl   1/1       Running   0          1d
es-master-78f97f98d9-kwqxt   1/1       Running   0          1d
es-master-78f97f98d9-lp6bn   1/1       Running   0          1d
```

You can see whether the data nodes are successfully running by checking the log output of any of these data nodes using the command:

```
kubectl -n elasticsearch logs -f es-data-0
```

If the log output contains the following message, it means that Elasticsearch data nodes have clustered successfully and are ready to start indexing data:
`[2019-04-04T06:37:57,208][INFO ][o.e.c.s.ClusterApplierService] [es-data-0] detected_master {es-master-78f97f98d9-kwqxt}`

At this point the cluster has been successfully deployed, but you still need to initialize it with the default users and their passwords.

### Cluster Security Initialization

As described in the [documentation for Open Distro for Elasticsearch](https://opendistro.github.io/for-elasticsearch-docs/docs/install/docker-security/), after deployment a cluster has to be initialized with security before it can be made available for use. This is done through two files that reside on the containers running Elasticsearch.

To start the initialization process, use the following command to gain shell access to one of master nodes:

```
kubectl -n elasticsearch exec -it es-master-78f97f98d9-275sl -- bash
```

Once inside, navigate to `/usr/share/elasticsearch/plugins/opendistro_security/tools` and execute the following command:

```
chmod +x hash.sh
```

This will make the password hashing script executable. Now we will use this script to generate bcrypt hashed passwords for our default users. The default users can be seen in file `/usr/share/elasticsearch/plugins/opendistro_security/securityconfig/internal_users.yml` which by default looks like:

```
# This is the internal user database
# The hash value is a bcrypt hash and can be generated with plugin/tools/hash.sh

# Still using default password: admin
admin:
  readonly: true
  hash: $2y$12$SFNvhLHf7MPCpRCq00o/BuU8GMdcD.7BymhT80YHNISBHsfJwhTou
  roles:
    - admin
  attributes:
    #no dots allowed in attribute names
    attribute1: value1
    attribute2: value2
    attribute3: value3

# Still using default password: logstash
logstash:
  hash: $2a$12$u1ShR4l4uBS3Uv59Pa2y5.1uQuZBrZtmNfqB3iM/.jL0XoV9sghS2
  roles:
    - logstash

# New password applied
kibanaserver:
  readonly: true
  hash: $2a$12$4AcgAt3xwOWadA5s5blL6ev39OXDNhmOesEoo33eZtrq2N0YrU3H.

# Still using default password: kibanaro
kibanaro:
  hash: $2a$12$JJSXNfTowz7Uu5ttXfeYpeYE0arACvcwlPBStB1F.MI7f0U9Z4DGC
  roles:
    - kibanauser
    - readall

# Still using default password: readall
readall:
  hash: $2a$12$ae4ycwzwvLtZxwZ82RmiEunBbIPiAmGZduBAjKN0TXdwQFtCwARz2
  #password is: readall
  roles:
    - readall

# Still using default password: snapshotrestore
snapshotrestore:
  hash: $2y$12$DpwmetHKwgYnorbgdvORCenv4NAK8cPUg8AI6pxLCuWf/ALc0.v7W
  roles:
    - snapshotrestore
```

To change the passwords in the `internal_users.yml` file, start by generating hashed passwords for each user in the file using the `hash.sh` script. Use the following command:

```
./hash.sh -p <password you want to hash>
```

For example, if I want to change the password of the admin user, I would do the following:

```
[root@es-master-78f97f98d9-275sl tools]# ./hash.sh -p ThisIsAStrongPassword9876212
$2y$12$yMchvPrjvqbwweYihFiDyePfUj3CEqgps3X1ACciPjtbibGUExsiu
```

The output string is the bcrypt hashed password. We will now replace the hash for admin user in the `internal_users.yml` file with this hash, resulting in the file looking like this:

```
# This is the internal user database
# The hash value is a bcrypt hash and can be generated with plugin/tools/hash.sh

# Password changed for user admin
admin:
  readonly: true
  hash: $2y$12$yMchvPrjvqbwweYihFiDyePfUj3CEqgps3X1ACciPjtbibGUExsiu
  roles:
    - admin
  attributes:
    #no dots allowed in attribute names
    attribute1: value1
    attribute2: value2
    attribute3: value3

# Still using default password: logstash
logstash:
  hash: $2a$12$u1ShR4l4uBS3Uv59Pa2y5.1uQuZBrZtmNfqB3iM/.jL0XoV9sghS2
  roles:
    - logstash

# New password applied
kibanaserver:
  readonly: true
  hash: $2a$12$4AcgAt3xwOWadA5s5blL6ev39OXDNhmOesEoo33eZtrq2N0YrU3H.

# Still using default password: kibanaro
kibanaro:
  hash: $2a$12$JJSXNfTowz7Uu5ttXfeYpeYE0arACvcwlPBStB1F.MI7f0U9Z4DGC
  roles:
    - kibanauser
    - readall

# Still using default password: readall
readall:
  hash: $2a$12$ae4ycwzwvLtZxwZ82RmiEunBbIPiAmGZduBAjKN0TXdwQFtCwARz2
  #password is: readall
  roles:
    - readall

# Still using default password: snapshotrestore
snapshotrestore:
  hash: $2y$12$DpwmetHKwgYnorbgdvORCenv4NAK8cPUg8AI6pxLCuWf/ALc0.v7W
  roles:
    - snapshotrestore
```

Do this for each default user in this file and store the plaintext version of the password securely, as some of these will be required in future deployment.

Initialize using `/usr/share/elasticsearch/plugins/opendistro_security/tools/securityadmin.sh` script.

The initialization command requires certain parameters, and should look like this:
`/usr/share/elasticsearch/plugins/opendistro_security/tools/securityadmin.sh -cacert /usr/share/elasticsearch/config/admin-root-ca.pem -cert /usr/share/elasticsearch/config/admin-crt.pem -key /usr/share/elasticsearch/config/admin-key.pem -cd /usr/share/elasticsearch/plugins/opendistro_security/securityconfig/ -keypass <replace-with-passphrase-for-admin-private-key> -h <replace-with-IP-of-master-nodes> -nhnv -icl`

This command specifies what admin client TLS certificate and private key to use to execute the script successfully. This are the second set of certificates that we loaded earlier as part of the ConfigMap. The -cd flag specifies the directory in which the initialization configs are stored. The -keypass flag must be set to the passphrase chosen when the admin client private key was generated. The -h flag specifies what hostname to use, in this case the internal IP address of the pod we're shelling into.

If it runs successfully and is able to initialize the cluster, the output will look like the following:

```
Open Distro Security Admin v6
Will connect to 10.30.128.125:9300 ... done
Elasticsearch Version: 6.5.4
Open Distro Security Version: 0.7.0.1
Connected as CN=admin.example.com
Contacting elasticsearch cluster 'elasticsearch' and wait for YELLOW clusterstate ...
Clustername: logs
Clusterstate: GREEN
Number of nodes: 8
Number of data nodes: 3
.opendistro_security index already exists, so we do not need to create one.
Populate config from /usr/share/elasticsearch/plugins/opendistro_security/securityconfig/
Will update 'security/config' with /usr/share/elasticsearch/plugins/opendistro_security/securityconfig/config.yml
   SUCC: Configuration for 'config' created or updated
Will update 'security/roles' with /usr/share/elasticsearch/plugins/opendistro_security/securityconfig/roles.yml
   SUCC: Configuration for 'roles' created or updated
Will update 'security/rolesmapping' with /usr/share/elasticsearch/plugins/opendistro_security/securityconfig/roles_mapping.yml
   SUCC: Configuration for 'rolesmapping' created or updated
Will update 'security/internalusers' with /usr/share/elasticsearch/plugins/opendistro_security/securityconfig/internal_users.yml
   SUCC: Configuration for 'internalusers' created or updated
Will update 'security/actiongroups' with /usr/share/elasticsearch/plugins/opendistro_security/securityconfig/action_groups.yml
   SUCC: Configuration for 'actiongroups' created or updated
Done with success
```

Your Elasticsearch cluster has now been successfully deployed, configured, and initialized!

## Kibana Deployment

Start deploying Kibana now using the following commands:

```
kubectl apply -f 10-kb-namespace.yml
kubectl apply -f 20-kb-configmap.yml
kubectl apply -f 30-kb-deploy.yml
kubectl apply -f 40-kb-service.yml
```

Kibana will take a few moments to get up and running.

You should be able to access the Kibana UI on [https://kibana.sec.example.com](https://kibana.sec.example.com/).

## Acknowledgements

* [Zack Doherty](https://github.com/zdoherty) (Senior SRE - Tinder Engineering) for all his help with Kubernetes internals
* [Pires](https://github.com/pires) for his work on the Open-source Elasticsearch deployment in Kubernetes
* Open Distro for Elasticsearch team for their support and guidance in writing this AWS Blog Post
* Ring Security Team for their support and encouragement
