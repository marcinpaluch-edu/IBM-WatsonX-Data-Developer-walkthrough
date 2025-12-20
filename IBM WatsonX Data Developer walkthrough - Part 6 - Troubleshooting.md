## Part 6. WatsonX.data Developer - Troubleshooting guide

This document collects various hints, tips and tricks in case your installation on WatsonX.data required troubleshooting. 

List of contents:
- [6.1. Solving error catalog xxx does not exist](#61-error-catalog-iceberg_data-does-not-exist)

### 6.1. Error Catalog iceberg_data does not exist.
This error happened many times on my laptop and I haven't yet figured out why it may happen. It's the problem with Presto, not the Iceberg tables. You log in into your WatsonX.data Developer UI like everyday but unexpectedly in the moment of browing your tables in the Data Manager view or Query workspace view those navigation tree items don't expand and you receive error popup messages on the right side of the screen, just like on the picture below:

![Error Catalog does not exist](img/wxd601_wxd_troubleshooting_catalog_does_not_exist.png)

In Powershell terminal started as Administrator run command:
```powershell
kubectl get pods -n wxd | Select-String lhams-api
```

The pod lhams-api should be running normally.

![lhams-api](img/wxd602_wxd_troubleshooting_powershell_get_lhadmin-api_pod.png)

Restart the pod's deployment with this command:

```powershell
kubectl rollout restart deploy/lhams-api -n wxd
```

![lhams-api deployment restarted](img/wxd603_wxd_troubleshooting_powershell_lhams_api_restart.png)

Then restart lhconsole-api pod with this command:

```powershell
kubectl rollout restart deploy/lhconsole-api -n wxd
```

![lhconsole restart](img/wxd604_wxd_troubleshooting_powershell_lhconsole-api_restart.png)

Then delete the ibm-lh-presto pod:

```powershell
kubectl delete pod -n wxd -l app=ibm-lh-presto
```

![Delete presto pod](img/wxd605_wxd_troubleshooting_powershell_delete_presto_pod.png)

See that new Presto pod was automatically deployed:

```powershell 
kubectl get pods -n wxd | Select-String ibm-lh-presto
```

![Check new Presto pod](img/wxd606_wxd_troubleshooting_powershell_new_presto_pod_deployed.png)

Then log into the new Presto pod shell:

```powershell
kubectl exec -n wxd -it deploy/ibm-lh-presto -- presto --server https://localhost:8443 --insecure --user ibmlhadmin --password
```

![Login to new Presto pod](img/wxd607_wxd_troubleshooting_powershell_login_to_new_prestopod.png)

In Presto, run few commands to see if the catalogs and tables were all recreated ok:

```sql
SHOW CATALOGS;
```

![Show catalogs in Presto](img/wxd608_wxd_troubleshooting_presto_show_catalogs.png)

and:

```sql
SHOW SCHEMAS FROM iceberg_data;
```
![Show schemas](img/wxd609_wxd_troubleshooting_presto_show_schemas.png)

You can exit:

```sql
exit
```

and go to the browser and see Data Manager or Query Workspace to confirm that all schemas and catalogs have been recreated from Apache Iceberg correctly. 

This is the end of Part 6. Troubleshooting.

[Back to Readme.md](./README.md)