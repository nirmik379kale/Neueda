
# Openstack Migration/Evacuation Automation With Ansible

This project helps you to migrate instances from one compute node to another available compute node.

The tasks in the ansible can be briefed as below:
- Listing Running instances on source compute node.
- Live migrating Running instances to other available compute host.
- Listing Non-running instances on source compute node if `migration_strategy` is migrate.
- Cold migrate non-running instances from source compute node if `migration_strategy` is migrate.
- Evacaute source compute node if `migration_strategy` is evacuate.
- Disable the source compute node for any future instance placement, if `disable_source_host` is set to *true*. 

## How to Execute
This playbook assumes that you have Openstack CLI installed and have access to Openstack Cloud API.

Before executing the playbook, you need to source the Openstack project `keystone.rc` to export all necessary Openstack env variables which this playbook will be using to communicate to Openstack API.
```
$ source keystone.rc
```

The playbook with all its variables defined can be executed in one of the following way
- Using Cold Migration Strategy
```
$  ansible-playbook -e '{source_host: "openstack-compute-02.us-reg01", migration_strategy: "migrate", disable_source_host: false}' os-migrate.yaml 
```
- Using Evacuation Strategy
```
$  ansible-playbook -e '{source_host: "openstack-compute-02.us-reg01", migration_strategy: "evacuate", disable_source_host: false}' os-migrate.yaml 
```
### Valid Values for Variables
```
- source_host           : compute-01-example.openstack.local
- migration_strategy    : migrate / evacuate
- disable_source_host   : true / false  
```

## Migration Strategies
The playbook expects one of two strategies to be used for migrating non-running instances from source compute node which are **MIGRATE** or **EVACUATE**.
- **MIGRATE** : If the `migration_strategy` is `migrate`, then the non-running instances will be cold migrated one by one to other available compute nodes using `openstack server migrate` utility.
- **EVACUATE** :  If the migration_strategy is evacuate, then the non-running instances will be evacuated all at once by schedular to other available compute nodes using `nova host-evacuate` utility.

These options are provided because `nova host-evacuate` can only be successfully executed if the source host is down/unreachable and the compute nodes have shared storage configured. In the case where this can not be emulated (e.g. for the purpose of this assignment), the cold migrate strategy makes more sense. 

## Disable Source Host
The playbook also have the variable to let you control the source compute node status by setting **disable_source_host**. If `disable_source_host` is set to `true`, the task will disable the source host status so schedular will not place any new instance on this node. It won't it set to `false`. 

## Managing TIMEOUT for Live Migration
The `--wait` flag is used during migration due to which the command completes only when the migration is completed, so migration timeout is implicitly managed.
The default values for `live_migration_timeout_action` and `live_migration_completion_timeout` in `nova.conf` are considered in this scenario. These can be changed as per requirement if the migration is expected to take longer than the default timeout value.
