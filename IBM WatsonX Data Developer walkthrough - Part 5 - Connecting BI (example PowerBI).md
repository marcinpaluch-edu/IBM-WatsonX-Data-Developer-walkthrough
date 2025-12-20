## Part 5. WatsonX.data Developer connected by BI tools - for example PowerBI

After successful ingestion of the data into WatsonX.Data Developer and building a model according to the Medallion Architecture (described in [Part 3. Data Ingestion](./IBM%20WatsonX%20Data%20Developer%20walkthrough%20-%20Part%203%20-%20Data%20Ingestion.md) in this repository) the next step is to consume that data and one of the ways of consuming it is exposing it to business intelligence tools for BI analysis and dashboarding. This chapter will show how to connect PowerBI to WatsonX.data Developer-based Presto service. 

In the official WatsonX.data 
[documentation](https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-bi_intro) you can find two (2) ODBC engines mentioned, which can help you to connect to the Presto service inside of your WatsonX.data - Simba and CData. 

![](img/wxd501_connecting_powerbi_to_wxd_documentation.png)

Let's start from Simba ODBC Driver and I will also show CData driver next. 

5.1. First Simba. It's working more seamlessly with external ODBC connection-bound BI tools such as PowerBI as it allows to control metadata settings. The free trial is 20 days long and the license key will be sent to the email you provide during registration. Warning: gmail addresses won't be accepted! The page is [here](https://insightsoftware.com/drivers/presto-odbc-jdbc/).

![Simba ODBC driver producer page](img/wxd502_simba_odbc_vendorpage.png)

5.2. ODBC driver of Simba is very easy to configure: you need to name the DSN, set Authentication type to LDAP, provide with your default user and password to your watsonx.data developer edition, your forwarded host and forwarded port and then press SSL Options... button:

![Simba ODBC configuration](img/wxd503_simba_odbc_configuration.png)

In the SSL Options... check the Allow Self-signed Server Certificate option and press OK:

![Self-signed certificate acceptance](img/wxd504_simba_odbc_configuration.png)

At the end Test the connection: 

![Test connection](img/wxd505_simba_odbc_configuration_test_success.png)

Your Simba ODBC connection is now created:

![Simba ODBC connection listed](img/wxd506_simba_odbc_connection_created.png)

5.3. Now open your BI tool - let it be PowerBI and add new data source and select ODBC:

![PowerBI selecting ODBC source](img/wxd507_powerbi_add_odbc_connection.png)

In the ODBC drivers view, select your newly created Simba connection:

![Selecting Simba connection](img/wxd508_powerbi_add_odbc_connection_simba.png)

If this is the first time connection, you'll be asked your user login and password once again:

![Login to WatsonX.data Developer](img/wxd509_powerbi_add_odbc_connection_simba_login.png)

When you navigate down the tree to one of the gold tables, you'll see the table contents preview:

![Table preview](img/wxd510_powerbi_add_odbc_connection_simba_wxdtablepreview.png)

Select and load the table:

![Load the table](img/wxd511_powerbi_add_odbc_connection_simba_wxdtablepreview_load.png)

See the Presto table columns available:

![Presto columns loaded](img/wxd512_powerbi_add_odbc_connection_simba_wxdtable_loaded.png)

Start dashboarding!

![Start dashboarding](img/wxd513_powerbi_add_odbc_connection_simba_wxdtable_startdashboard.png)

5.4. In case your port wasn't open, make sure you port-forward to your localhost from your Presto pod. Check the Presto service is up first: 
```powershell
kubectl get services -n wxd
```
and forward the port:
```powershell
kubectl port-forward svc/ibm-lh-presto-svc 8443:8443 -n wxd
```

![Presto portforward](img/wxd514_powershell_presto_portforward.png)

5.5. The second suggested driver by the official documentation is not as successful and by the moment of writing this text I missed more information on how to configure it and Copilot or ChatGPT were sure this isn't possible to work with my Presto in WatsonX.data Developer. CData installs ok and you can configure it connects to your Presto ok but it's more complex to configure too. 

Configure your CDAta driver with your Presto host, port, user and password:

![CData settings](img/wxd515_cda_connectionconfiguration.png)

The configuration will require SSL Server Certificate added:

![CData SSL Server Cert](img/wxd516_cdata_connectionconfiguration_sslservercert.png)

How to find it? Go to your WatsonX.Data Developer and navigate to Access Control:

![Navigate to Access Control](img/wxd517_wxd_ui_toaccesscontrol.png)

In Access Control find Presto and press Manage access:

![Access Control view](img/wxd518_wxd_ui_accesscontrol.png)

You'll see Presto instance view. Press View connect details:

![Presto instance view](img/wxd519_wxd_ui_accesscontrol_presto_instanceview.png)

On the left panel find SSL certificate and copy it to the clipboard:

![Copy SSL certificate](img/wxd520_wxd_ui_accesscontrol_presto_instanceview_copysslcertificate.png)

![CData Test connection success](img/wxd521_cdata_testconnectionsuccess.png)

My problem was though that I couldn't have see my columns in the tables in Presto in the Metadata tab in CData Data Model Object Explorer:

![Columns error](img/wxd522_cdata_columnsfailederror.png)

The problem manifests later on in PowerBI too and the table in effect won't load into PowerBI at all:

![Columns error in PowerBI](img/wxd523_powerbi_columnserror.png)

![Final error](img/wxd524_powerbi_columnserror_finalerror.png)

A workaround exists by creating manually User views, means custom ```SELECT``` statements in the Data Model Object Explorer in the CData ODBC driver but that means additional effort and maintainance and it's not something we want to be doing on production later on. 

This is the end of Part 5. Connecting BI (example PowerBI).

[Back to Readme.md](./README.md)