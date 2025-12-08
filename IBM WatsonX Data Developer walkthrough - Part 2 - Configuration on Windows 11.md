## Part 2. WatsonX.data Developer Configuration

In [Part 1. WatsonX.data Developer Installation](./IBM%20WatsonX%20Data%20Developer%20walkthrough%20-%20Part%201%20-%20Installation%20on%20Windows%2011.md) I described the necessary steps to install WatsonX.data Developer Edition version 1.0.0 on Windows 11 OS. This part will focus on further configuration of the data sources and your first data ingestion into Apache Iceberg.

### I. Connecting to internal postgres
You may have noticed that WatsonX.data Developer comes with built-in pod containing Postgres database. It is intended for internal use but you may want to understand if there's any way to connect to it or perhaps to use it for learning purposes. Here's the way.

2.1. Run this command to check details for your built-in postgres database
```powershell
kubectl get configmap wxd-launch-cm -n wxd -o yaml | Select-String POSTGRES
```

![kubectl get configmap](img/wxd201_powershell_kubectl_get_configmap.png)

2.2. Use the obtained details to connect to the database server. Go to the Infrastructure manager and click ```Add Component``` button on the right to add the Dummy database to your Data sources:
![Add component to infrastructure](img/wxd202_gui_infrastructuremanager_addcomponent.png)

2.3. Pick the PostgreSQL from the components catalog and press Next.
![Select PostgreSQL component](img/wxd203_gui_infrastructuremanager_addcomponent_PostgreSQL_select.png)

2.4. Fill in the form with the ```dummy``` Postgres database details obtained in the previous step and test the connection. Then press Create.
![Dummy Postgres database parameters test](img/wxd204_gui_infrastructuremanager_dummydatabase_test.png)

2.5. Dummy postgres database is now added to the Infrastructure manager as a new data source.
![New data source - dummy database](img/wxd205_gui_infrastructuremanager_dummydatabase_added.png)

2.6. Now connect the dummy postges db to the catalog. Hover over the icon of dummy PostgreSQL data source and click the Plus icon.
![Press Add Catalog](img/wxd206_gui_infrastructuremanager_addcatalog_to_dummypostgres.png)

2.7. Name the catalog, i.e. Dummy catalog and press Add
![Naming catalog](img/wxd207_gui_infrastructuremanager_addcatalog_dummycatalog.png)

2.8. The new catalog is now created.
![Dummy catalog created](img/wxd208_gui_infrastructuremanager_dummycatalog_created.png)

2.9. Hover your mouse over the dummy catalog and over the connector and click Manage Associations
![Manage associations](img/wxd209_gui_infrastructuremanager_dummycatalog_manageassociations.png)

2.10. Select association to Presto-01 and press Save and restart engine
![Select Presto](img/wxd210_gui_infrastructuremanager_dummycatalog_selectpresto01.png)

2.11. The dummy postgres db is now connected with Presto and is ready to query along with other data sources
![Dummy postgres now associated](img/wxd211_gui_infrastructuremanager_dummycatalog_associated_withpresto.png)

2.12. Navigate to Data manager
![Navigate to data manager](img/wxd212_gui_infrastructuremanager_navigatetodatamanager.png)

2.13. See the dummy PostgreSQL database entry with its tables, ready to use in the query
![Dummy postgreSQL db visible in Data manager](img/wxd213_gui_datamanager_dummypostgresview.png)

2.14. You won't be able to expand the schema of your postgres database in the GUI of WatsonX.data Developer. You need to do it via the native PostgreSQL client, such as ```psql```. Find and connect to the pod containing your dummy postgres database:
```powershell
kubectl get pods -n wxd | findstr postgres
```
![Find postgres pod in wxd](img/wxd214_powershell_kubectl_getpods_withpostgres.png)

2.15. Log in to the pod ```wxd-pg-postgres-0``` with kubectl and then login to the postgres database dummy with psql client:

```powershell
kubectl exec -it wxd-pg-postgres-0 -n wxd -- sh
```

```psql
psql "host=localhost port=5432 user=dummy_user password=dummy dbname=dummy"
```

![Login to postgres](img/wxd215_powershell_logintothepostgrespod_andrunpsql.png)

2.16. Create my_schema schema, test table and insert "example" value into it
![Example data insert](img/wxd216_psql_createschema_table_and_insertexamplevalue.png)

2.17. Find the created table in the WatsonX.data Developer GUI - refresh the dummy_catalog, then find my_schema and test table within. Click ```test``` table and navigate to Data sample tab to see the example value inserted into it.
![Viewing inserted data in WatsonX.data](img/wxd217_gui_find_myschema_testtable_andexamplevalue.png)

### II. Ingestion of data into Apache Iceberg

2.18. Let's try now ingestion into Apache Iceberg. Ingesting data into Iceberg gives you a single, high-performance, governed, AI-ready data layer—no matter where the data originally lives. Bringing your data into iceberg will safe your original data from querying, make it independent of schema evolutions, and will enable audit-ready time travel and rollback capability. This is important for BI dashboards or machine learning training. You decouple storage from compute which is cost advantage too. This is different concept of Ingestion from federation. Press the Ingest data button on far right:
![Press Ingest data button](img/wxd218_gui_ingestdata_intoiceberg_button.png)

2.19. Fill in the form by pointing at just created my_schema schema, test table and example value in dummy postgreSQL database. At the end press Done:
![Configure ingestion](img/wxd219_gui_ingestdata_intoiceberg_form.png) 

2.20. The ingestion job will be first Accepted and then get into Running state:
![Ingestion job running](img/wxd220_gui_ingestdata_jobaccepted.png)

2.21. When the job is Finished, you can quick navigate to the newly created table in Apache Iceberg:
![Ingestion job finished](img/wxd221_gui_ingestdata_jobcompleted.png)

2.22. Go to the Data Sample tab to see the example value copied over from Postgres to Apache Iceberg:
![Example value copied](img/wxd222_gui_ingestdata_testtable_andexamplevalue_inicberg_ingested.png)


### III. Configuring external data sources

Let's imagine I have Postgres database server installed outside of the kind cluster, directly on my Windows laptop, the same where I installed watsonx.data. I'd like to connect to that Postgres database from my WatsonX.data Developer installation and ingest data from it. How do I connect? There are few steps to think about to make it work.

I find this part very specific to Windows 11. There are no similar issues on MacOS. Connecting to a Postgres database from inside of WatsonX.data Developer, deployed on MacOS, simply works by pointing to ```host.containers.internal``` as the database's hostname.

On Windows it doesn't work as there's additional layer of WSL2 with additional routing. The ```host.containers.internal``` name resolution still exists but it points to WSL2 virtual machine, not Windows OS. You can find it's value in the ```kind-wxd-control-plane``` cluster. Let's just take a look.

2.23. Run these commands in powershell to test the usual hostname host.containers.internal:

```powershell
podman ps
```

then connect to it:
```powershell
podman exec -it kind-wxd-control-plane sh
```

then inside the container, see the ```/etc/hosts``` contents:
```shell
cat /etc/hosts
```

![Checking value of host.containers.internal](img/wxd223_powershell_check_hostcontainersinternal_value.png)


2.25. So the value exists. But unlike on MacOS, connection to that host in Windows installation will fail:
![host.containers.internal connection fails](img/wxd224_GUI_hostcontainersinternal_connectionfails.png)

2.26. Back to the container, you may want to check if the port is even reachable from it. Run the command:
```shell
nc -vz host.containers.internal 5432
```

Warning: if you miss ```netcat``` binaries in your podman, which is likely, install it with commands:
```shell
apt update
apt install -y netcat-openbsd
```
This is the output you're going to see:
![podman shell netcat test](img/wxd226_podmanshell_hostcontainersinternal_connectionfails.png)

In MacOS it would already work. On Windows 11 it needs another approach. This is becase the Windows installation of WatsonX.data Developer has the following structure:  

```
Windows Host
 ├── PostgreSQL running on 127.0.0.1:5432
 ├── WSL Ubuntu (separate VM)  ← your terminal
 └── Podman Machine (FCOS VM)  ← your Kubernetes pods
```

2.27. Run the wsl command in powershell:
```powershell
wsl
```
and then inside wsl, run:
```bash
ip route show default
```
You'll get your Windows host IP as seen from WSL:
![Windows host IP as seen from WSL](img/wxd227_powershell_wsl_checkWindowshostIPasseenfromWSL.png)

This is your gateway to your locally installed PostgreSQL database server, located on Windows. from WatsonX.Data Developer.

2.28. Test the obtained IP with netcat command from your podman kind cluster:
```shell
nc -vz <Windows-IP-by-WSL> 5432
```

and voila!
![Windows IP by WSL works](img/wxd228_podmanshell_windowsIPbyWSL_connectionsucceeds.png)

2.29. Check also in the WatsonX.data Developer GUI:
![Test in GUI](img/wxd229_GUI_checkWindowshostIPasseenfromWSL.png)

2.30. There are additional considerations for Windows:
- configuration of your Windows Firewall rules
- configuration of your Postgres server

Let's see the Firewall rules. You need to have open  firewall rule to let inbound requests arrive to your postgres database server, installed directly on your Windows OS. 

Check if your Postgres is working ok and is reachable on Windows on the localhost hostname and the default 5432 port:

```powershell
Test-NetConnection -Port 5432 -ComputerName localhost
```
The expected result:
![Postgres localhost and 5432 port test](img/wxd230_powershell_checkonWindowsPGislocalhostAnd5432.png)

2.31. If your Postgres runs fine on your Windows machine as the localhost host and 5432 port service but is blocked by the firewall from inbound traffic from your WSL, then open that port. Run in powershell:
```powershell
New-NetFirewallRule -DisplayName "PostgreSQL WSL" -Direction Inbound -LocalPort 5432 -Protocol TCP -Action Allow
```

If you prefer less liberal approach and only inbound traffic from the WSL network is allowed, run rather this line:
```powershell
New-NetFirewallRule -DisplayName "PostgreSQL WSL" -Direction Inbound -LocalPort 5432 -Protocol TCP -Action Allow -RemoteAddress 172.19.0.0/16
```

![Create firewall rule](img/wxd231_powershell_createfirewallruleforpostgresfromwsl.png)

Then run your netcat command from your podman kind cluster again to see if the connection now works.

```shell
nc -vz 172.19.48.1 5432
```

2.32. If the firewall rule was created but connection to the PostgreSQL database server wasn't enabled, one more thing to check is the Postgres itself configuration in pg_hba.conf file. 

Edit ```pg_hba.conf```. It is usually inside directory ```C:\Program Files\PostgreSQL\<yourversion>\data```.  

Add these lines as the first lines:
```conf
# Allow Watsonx / KIND / WSL2 pods to connect
host    all    			all    			xxx.xxx.0.0/16    		scram-sha-256
```
where xxx.xxx.0.0 is the network to which your Windows OS IP belong to according to your WSL.

![How your pg_hba.conf should look like](img/wxd232_pg_hbaconf.png)

and then restart your Postgres server:
```powershell
net stop postgresql-x64-<yourversion>
net start postgresql-x64-<yourversion>
```

2.33. Bonus - if you wanted to double-double check your connection from your podman kind container, without checking it from the WatsonX.data Developer, just install postgres client on it and try to log in:

```shell
sudo apt update
sudo apt install postgresql-client
```

And then:
```shell
psql -h <your Windows IP> -U postgres
```

This is how it will go:
![Logging into postgres on Windows localhost from podman kind cluster](img/wxd233_shell_podmankindcontainer_installpgclient.png)

2.34. Verify your localhost Postgres can be configured now ok but adding it to the Infrastructure manager as a new component:
![Final view with external Postgres](img/wxd234_postgres_total3dbs_added_view.png)

### IV. Configuring external data sources - outside of the localhost
Connection to any database or data source located outside of the local Windows OS host will require performing additional system, network and security configuration steps. 
But it is not subject of this material. 

This is the end of Part 2. Configuration.

[Back to Readme.md](./README.md)