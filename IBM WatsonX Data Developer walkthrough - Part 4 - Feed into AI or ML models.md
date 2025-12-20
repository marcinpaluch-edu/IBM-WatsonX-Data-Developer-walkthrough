## Part 4. WatsonX.data Developer outputs feed into AI/ML model

In [Part 3. Data Ingestion](./IBM%20WatsonX%20Data%20Developer%20walkthrough%20-%20Part%203%20-%20Data%20Ingestion.md) I did show how to process new data through 3 layers: bronze, silver and gold, in WatsonX.data Developer. In this part I will show how to connect to WatsonX.data, both Developer local install and IBM Cloud-based SaaS system, to use the data collected in the Iceberg tables in AI/ML models.

Part 4. will consist of the following chapters:
[4.1. Connecting Watsonx.data Developer local laptop Presto with custom Python code](#41-connecting-from-custom-python-code)
[4.2. Connecting SaaS WatsonX.data Presto with SaaS WatsonX.ai jupyter notebook](#42-connecting-from-watsonxai-jupyter-notebook)
[4.3. Connecting SaaS WatsonX.data Presto with SaaS WatsonX.ai data refinery project](#43-connecting-from-watsonxai-for-data-preparation-refinery-and-visualisation)

Let's start!

### 4.1. Connecting from custom Python code
4.1.1. Connecting from custom Python code requires access to the WatsonX.data Presto pod port from the machine where you run the Python code. Assuming you run your Python code on your local Windows OS and your WatsonX.data Developer Presto server runs in one of the pods on the kind cluster in podman in its own virtual network, your first step is to forward the Presto's port to Windows. Open Powershell as Administrator and run the port-forward command:

```powershell
kubectl port-forward svc/ibm-lh-presto-svc 8443:8443 -n wxd
```

![Port forward the Presto port](img/wxd401_powershell_portforward_prestopodport_to_windows.png)

4.1.2. Now you need a custom Python code to test the connection. Warning: Python 3.x is no longer compatible with Presto drivers and you need to import Trino  drivers instead.
```powershell
pip install trino pandas
```

4.1.3. Presto within WatsonX.data Developer pod has a couple of characteristics to remember about:
- the port needs to be forwarded to the localhost or you deploy your code to the pod linux machine
- the server runs self-signed certificate
- authentication is basic - just provide with user and password, the same that you use to login to WatsonX.data UI.
- the connection requires SSL (https)
- the username needs also to be provided in the HTTP headers

With that, see the code to test the connection:

```python
import trino
import pandas as pd
import urllib3
import requests

# Disable SSL warnings (dev only)
urllib3.disable_warnings()

TRINO_USER = "ibmlhadmin"
TRINO_PASSWORD = "password"

# Custom session to inject LEGACY IBM header
session = requests.Session()
session.verify = False                       # self-signed cert
session.headers.update({
    "X-Presto-User": TRINO_USER              # REQUIRED by IBM /engine
})

conn = trino.dbapi.connect(
    host="localhost", #if you run from Windows locally
    port=8443,     # the forwarded or actual port
    http_scheme="https",
    user=TRINO_USER,
    auth=trino.auth.BasicAuthentication(TRINO_USER, TRINO_PASSWORD),
    verify=False,
    catalog="iceberg_data",
    schema="gold"
)

conn._http_session = session
conn._http_session.base_url = "https://localhost:8443/engine"

cursor = conn.cursor()

# Send test query
cursor.execute("SHOW CATALOGS")
print(cursor.fetchall())

cursor.execute("SHOW SCHEMAS FROM iceberg_data")
print(cursor.fetchall())

cursor.execute("SHOW TABLES FROM iceberg_data.gold")
print(cursor.fetchall())
```

You can also download the file from [here](src/test_wxd_conn.py).

4.1.4. Run the Python program:
```powershell
python.exe .\test_wxd_conn.py
```

and see that in result the catalogs and schemas and two tables in schema gold are returned to the terminal:

![Python code test connection successfully](img/wxd402_powershell_test_prestoconn_in_python.png)

The connection is working and now you can play around the data You stored in the Apache Iceberg tables and made available via Presto engine in WatsonX.data Developer free edition. Create an ML/AI code of your choice.

### 4.2. Connecting from WatsonX.ai Jupyter Notebook
This is not a scenario to play with your free WatsonX.data Developer studio, downloaded on your Windows laptop. Instead you can play with it by using the full suite of WatsonX products, which you can now try for free on IBM Cloud. 

4.2.1. Since we're going to be connecting to IBM Cloud (SaaS) WatsonX.data installation, we need a fresh API key. Go to the IAM settings right after you logged into your IBM Cloud account.
![Go to IBM Cloud IAM](img/wxd403_ibmcloud_gotoIAM.png)

4.2.2. In the Access module go to the API keys and press Create + button to create new API key for your new WatsonX.ai application

![Go to create new API key](img/wxd404_ibmcloud_gotoAPIKeys.png)

4.2.3. Give the new API key a name and press Create button

![Create new API key](img/wxd405_ibmcloud_createnewAPIkey.png)

4.2.4. Copy the newly created API key to clipboard. You'll need it in your Jupyter notebook application in WatsonX.ai

![Copy API key](img/wxd406_ibmcloud_copyAPIkey_toclipboard.png)


4.2.5. Navigate to WatsonX on IBM Cloud (WatsonX on SaaS):

![](img/wxd407_ibmcloud_navigatetowatsonx.png)

Launch WatsonX:

![](img/wxd408_ibmcloud_launch_watsonx.png)

Give it a moment to load:

![](img/wxd409_ibmcloud_loadingupwatsonx.png)

Skip the tour:

![](img/wxd410_watsonxsaas_loaded_skiptour.png)

Ignore initial tasks:

![](img/wxd411_watsonxsaas_skipinitialtasks.png)

4.2.6. Once in WatsonX, go to Projects:

![](img/wxd412_watsonxsaas_gotoprojects.png)

4.2.7. Create new project

![](img/wxd413_watsonxsaas_projectslist_clickNew.png)

4.2.8. Fill in with your favorite project name and you can leave the selected Python kernel unchanged:

![](img/wxd414_watsonxsaas_creatingnewproject.png)

4.2.9. Once the project was creared, click Assets tab to add the notebook:

![](img/wxd415_watsonxsaas_newprojectview_clickassets.png)

4.2.10. Click New Assset + button

![](img/wxd416_watsonxsaas_clicknewasset.png)

4.2.11. Start typing jupyter into the search field to navigate quick to the notebooks creation wizard:

![](img/wxd417_watsonxsaas_findjupyternotebookcategory.png)

4.2.12. Give the notebook new name and press Create button:

![](img/wxd418_watsonxsaas_addingnewnotebook.png)

Give it a moment for the notebook to load:

![](img/wxd419_watsonxsaas_loadingnewnotebookprogress.png)

4.2.13. New notebook in now loaded:

![](img/wxd420_newnotebookloaded.png)

4.2.14. You'll first need to install trino driver or make sure one was previously installed for your Python. Provide with command into the first command cell:

```python
!pip install trino
```

![](img/wxd421_watsonxsaas_installingtrinoviapip.png)

4.2.15. After successfull installation of trino, run the script similar to the one you created for your local installation of WatsonX.data Developer, this time for WatsonX.data on IBM Cloud (SaaS):

```python
from trino.dbapi import connect
from trino.auth import JWTAuthentication

# ===== CONFIG =====
HOST = "<change_to_your_watsonxdata_hostname>"   # e.g. <instance>.lakehouse.cloud.ibm.com
PORT = 443
CATALOG = "iceberg_data"              # or hive_data, sample_data, etc.
SCHEMA = "default"
TRINO_USER = "<change_to_your_username>"             # often required even with token
IBM_API_KEY = "<change_to_your_apikey>"


import requests

url = "https://iam.cloud.ibm.com/identity/token"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
}

data = {
    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    "apikey": IBM_API_KEY,
}

r = requests.post(url, headers=headers, data=data)

print("Status:", r.status_code)
# print("Response:", r.text)

r.raise_for_status()

access_token = r.json()["access_token"]
# print("Token starts with:", access_token[:30])

# Custom session to inject LEGACY IBM header
session = requests.Session()
session.verify = False                       # self-signed cert
session.headers.update({
    "X-Presto-User": TRINO_USER              # REQUIRED by IBM /engine
})

conn = connect(
    host=HOST,
    port=PORT,
    http_scheme="https",
    user=TRINO_USER,
    catalog=CATALOG,
    schema=SCHEMA,
    auth=JWTAuthentication(access_token),
    verify=False,
)

conn._http_session = session

cur = conn.cursor()

# 1️. Identity check (MOST IMPORTANT)
cur.execute("SELECT current_user")
print("current_user =", cur.fetchall())

# 2️. Metadata
cur.execute("SHOW CATALOGS")
print("catalogs =", cur.fetchall())

# 3️. Simple query
cur.execute("SELECT 1")
print("select 1 =", cur.fetchall())

cur.close()
conn.close()
```

![](img/wxd422_watsonxsaas_connectiontestpythonscript_executedok.png)

4.2.16. You can now keep developing new code in this notebook and make further use of your data in WatsonX.data SaaS in WatsonX.ai runtime for ML/DS/AI activities. 

4.2.17. If you don't know what value for the host should be:
```python
HOST = "<change_to_your_watsonxdata_hostname>"   # e.g. <instance>.lakehouse.cloud.ibm.com
```
check it in the WatsonX.data. This is how to find it:

Click the 9 dots square in the top-right corner:

![](img/wxd423_watsonxsaas_navigatetootherproducts.png)

Select watsonx.data:

![](img/wxd424_watsonxsaas_navigatetowatsonxdata.png)

Make sure your project where the notebook is was selected and click the first link View engines in the Infrastructure manager:

![](img/wxd425_watsonxsaas_makesuretherightprojectiselected.png)

Log in:

![](img/wxd426_watsonxsaas_logintowatsonxdata.png)

Press the "burger" menu icon:

![](img/wxd427_watsonxdatasaas_openmenu.png)

Select Infrastructure manager from the left menu:

![](img/wxd428_watsonxdata_selectinfrastructuremanager.png)

In the Infrastructure manager click on Presto engine:

![](img/wxd429_watsonxdata_clickyourprestoengine.png)

Press View connection details link:

![](img/wxd430_watsonxdata_prestoenginedetailsview.png)

Find the hostname (1), which includes the instanceID, then port (2) and your username (3) to be used in your Python script:

![](img/wxd431_watsonxdata_yourprestohostname_copytoclipboard.png)

### 4.3. Connecting from WatsonX.ai for Data Preparation, refinery and visualisation

In this chapter I will connect to my SaaS-based (IBM Cloud) WatsonX.data Presto engine.

4.3.1. Navigate back to WatsonX.ai and see all projects and click the project you want. I'll select project where I just created the Notebook:

![](img/wxd433_watsonxsaas_navigatebacktoprojects.png)

4.3.2. Navigate to Assets and press New Asset button:

![](img/wxd434_watsonxsaas_Createnewasset.png)

4.3.3. Search for Data and select Create new data source:

![](img/wxd435_watsonxsaas_searchfordataassets.png)

4.3.4. Search for Presto and select IBM Watsonx.data

![](img/wxd436_watsonxsaas_selectwatsonxdata_asdatasource.png)

4.3.5. Press the tile IBM WatsonX.data Presto:

![](img/wxd437_watsonxsaas_selectwxdpresto_andnext.png)

4.3.6. In the first tab Connection Overview give the connection the name of your choice:

![](img/wxd438_watsonxsaas_givedatasourcename.png)

4.3.7. In the next tab Connection Details, select from dropdown the option IBM Watsonx.data on IBM Cloud and provide with your instance hostname, port, CRN:

![](img/wxd439_watsonxsaas_providewithhostportandcrn_todetails.png)

Should you wonder which host, port to provide and where to find CRN - go back to WatsonX.data Infrastructure Manager and find those details in your Presto engine graph item:

![](img/wxd440_watsonxsaas_hostportcrntouse.png)

4.3.8. Make sure the SSL is enabled and provide with your Presto SSL certificate. Paste also your API key you created before (or create a new one):

![](img/wxd441_watsonxsaas_credentialsandcertificatessl.png)

Reminder: you'll find your Presto SSL certificate in the same place:

![](img/wxd442_watsonxsaas_sslcertificatetocopy.png)

4.3.9. Engine connection details - provide with engine host, port and ID:

![](img/wxd443_watsonxsaas_engineconnectiondetails.png)

Reminder: the Presto Engine details can be found in the same Connection details page in Watsonx.data, just on the right hand side:

![](img/wxd444_watsonxsaas_engineconnectiondetails_tocopyfrom.png)

One step before you'll see value of EngineID - copy it from there:

![](img/wxd444b_watsonxsaas_engineid_tocopyfrom.png)

4.3.10. Configure where the data should be stored and the data sovereignty and press Test Connection:

![](img/wxd445_watsonxsaas_location_sovereignty_andpressTestConnection.png)

4.3.11. Connection should show all successful. If this is not the case, check all connection details once again. Otherwise press Create blue button:

![](img/wxd446_watsonxsaas_connectionsuccessful_gonext.png)

4.3.12. One Data source is created successfully, you can find it in your project assets. Go and create one more asset as the next step:

![](img/wxd447_watsonxsaas_connectioncreated_addnewassetagain.png)

4.3.13. Search for Data again and select Prepare and Visualize Data tile this time:

![](img/wxd448_watsonxsaas_searchfordata_selectprepareandvisualize.png)

4.3.14. Press the blue button: Select from Project:

![](img/wxd449_watsonxsaas_selectdatafromproject.png)

4.3.15. Navigate through the project Connection you just created all the way right to the table that you have stored in Apache Iceberg and is accessible now via your Presto connection. At the end press Select blue button:

![](img/wxd450_watsonxsaas_selectfinaltablefromwatsonxdata.png)

Should you wonder if the source table is the same as you wanted it, go back to Watsonx.data to check it in the original Iceberg_data catalog:

![](img/wxd451_watsonxsaas_originaltableinicebergforconfirmation.png)

4.3.16. Name your asset and press Create:

![](img/wxd452_watsonxsaas_givethedatasetname_presscreate.png)

4.3.17. It takes a while but the source table stored in your Watsonx.data Apache Iceberg gets accessed via Apache Presto and is visible for profiling and visualization in WatsonX:

![](img/wxd453_watsonxsaas_datasetcreated_outofwxdpresto.png)

Navigate via tabs to see the data profiling:

![](img/wxd454_watsonxsaas_dataprofile.png)

Check also the data visualisation options:

![](img/wxd455_watsonxsaas_datavisualisation.png)

You can further explore options to prepare, refine and visualize your data. The refined data can be used next in Watsonx.ai runtime for ML/AI/DS activities.

This is the end of Part 4. Feed into AI or ML models.

[Back to Readme.md](./README.md)