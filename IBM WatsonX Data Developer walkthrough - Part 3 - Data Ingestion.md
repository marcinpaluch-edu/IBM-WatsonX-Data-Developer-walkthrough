## Part 3. Medallion architecture

In [IBM WatsonX Data Developer walkthrough - Part 2 - Configuration on Windows 11](./IBM%20WatsonX%20Data%20Developer%20walkthrough%20-%20Part%202%20-%20Configuration%20on%20Windows%2011.md) I described the necessary steps to configure connections from WatsonX.data Developer Edition version 1.0.0 on Windows 11 OS to a locally available data source. In that case it was locally installed PostgreSQL server. I also demonstrated basics of data ingestion in WatsonX.data by using Spark engine and dummy Postgres database built into one of the pods of WatsonX.data Developer.  

In this part I will further focus on Data Ingestion. I will create new schemas configuration and organize all data into 3 layers: bronze, silver and gold, which follows so called Medallion Architecture, the design pattern for data lakehouses. 

### 3.1. Creating source database

3.1.1. I connect to my locally installed PostgreSQL database server and create new table in the default database ```postgres``` and in the default schema ```public``` to store simple data of client orders:

```sql
CREATE TABLE orders (
    id           BIGSERIAL PRIMARY KEY,
    customer_id  BIGINT NOT NULL,
    product_id   BIGINT NOT NULL,
    amount       NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
    currency     CHAR(3) NOT NULL,
    status       VARCHAR(32) NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_orders_customer_id ON orders (customer_id);
CREATE INDEX idx_orders_product_id  ON orders (product_id);
CREATE INDEX idx_orders_created_at  ON orders (created_at);


CREATE TYPE order_status AS ENUM ('pending', 'paid', 'shipped', 'cancelled');

ALTER TABLE orders
    ALTER COLUMN status TYPE order_status
    USING status::order_status;
```

I can check the creation of the datasource correctness in many ways, i.e. in the psql command-line tool for PostgreSQL:

![](img/wxd301_pgsql_sourcetablecreated.png)

3.1.2. Now I fill the database table with synthetic, generated orders. I insert 10 sample rows into the table: 
```sql
INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (1, 101, 1001, 49.99, 'USD', 'pending',  '2024-11-01 10:15:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (2, 102, 1002, 129.00, 'USD', 'paid',     '2024-11-01 11:03:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (3, 101, 1003, 19.50, 'EUR', 'paid',     '2024-11-02 09:42:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (4, 103, 1001, 49.99, 'EUR', 'cancelled','2024-11-02 14:10:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (5, 104, 1004, 299.99,'USD', 'paid',     '2024-11-03 16:55:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (6, 105, 1002, 129.00,'USD', 'shipped',  '2024-11-04 08:20:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (7, 101, 1005, 9.99,  'EUR', 'paid',     '2024-11-04 12:47:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (8, 106, 1003, 19.50, 'USD', 'pending',  '2024-11-05 18:30:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (9, 107, 1001, 49.99, 'USD', 'paid',     '2024-11-06 09:05:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (10,108, 1004, 299.99,'EUR', 'shipped',  '2024-11-06 15:40:00+00');
```

Again, I can see the inserted rows in many ways, this time in my pgAdmin UI tool:

![](img/wxd302_pgadmin_datainserted.png)

3.1.3. This ends my activities in the locally installed PostgreSQL database for time being

### 3.2. Create bronze layer in WatsonX.data Apache Iceberg

3.2.1. I switch now to my WatsonX.data Developer.

![Navigate to Query Workspace](img/wxd303_watsonxdata_navigatetoqueryworkspace.png)

In the Query Workspace I develop this SQL statement to create new schema and table for client orders, just this time in Apache Iceberg within WatsonX.data Developer. It's supposed to be identical, speaking of columns, with the table I just created in PostgreSQL server. The couple of extra columns I add - created at, ingested at or source, are for audit purposes. 

```sql
CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE bronze.orders_raw (
    id            BIGINT,
    customer_id   BIGINT,
    product_id    BIGINT,
    amount        DECIMAL(12,2),
    currency      VARCHAR(3),
    status        VARCHAR,
    created_at    TIMESTAMP WITH TIME ZONE,

    _ingested_at  TIMESTAMP WITH TIME ZONE,
    _source       VARCHAR
)
WITH (
    format = 'PARQUET'
);
```
The query:

![Developing SQL query](img/wxd304_runsqlcreatestatement_forbronze.png)

The schema bronze and table orders_raw are now created:

![Bronze and orders_raw created](img/wxd305_watsonxdata_bronzeschema_ordersrawtable_created.png)

3.2.2. Now I perform my first manual ingestion in Presto/Iceberg, by running new query. I have another option to configure my automatic ingestion in the Spark, and that is the correct way for large data volumes. On another hand, when I do the UI ingestion, it removes any unused columns like _ingested_at or _source as they don't exist in the source database table in PostgreSQL. Manual ingestion will preserve them.
This activity also demonstrates WatsonX.data's capability to federate access to various data sources in a single query:

```sql
INSERT INTO bronze.orders_raw (
    id,
    customer_id,
    product_id,
    amount,
    currency,
    status,
    created_at,
    _ingested_at,
    _source
)
SELECT
    id,
    customer_id,
    product_id,
    amount,
    CAST(currency AS VARCHAR(3)) AS currency,
    status,
    created_at,
    now()                        AS _ingested_at,
    'postgres.orders'            AS _source
FROM postgres.public.orders;
```
The view: 

![](img/wxd306_watsonxdata_manualingestion_fromorders_toordersraw.png)

In result, I have all rows from my source PostgreSQL database table ```orders``` now copied over to Apache Iceberg table ```bronze.orders_raw```:

![](img/wxd307_watsonxdata_manualingestionresult_populatedtable.png)

### 3.3. Create silver layer
3.3.1. It's time to create the 2nd layer: silver. My ```silver.orders_clean``` table will look like ```bronze.orders_raw``` but it will contain only those orders, which have status ```paid```. I'll create the table and populate it with values at the same step. This technique is called CTAS, means Create Table As Select:

```sql
CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE silver.orders_clean AS
SELECT
  id,
  customer_id,
  product_id,
  CAST(amount AS DOUBLE) AS amount,
  currency,
  created_at
FROM bronze.orders_raw
WHERE status = 'paid'
  AND amount > 0;
  ```

The query in Query Workspace looks the following:

![Create table as Select for silver.orders_clean](img/wxd308_watsonxdata_createsilver_and_ordersclean_asCTAS.png)

3.3.2. The table was created ok:

![](img/wxd309_watsonxdata_table_silver_ordersclean_created.png)

and populated:

![](img/wxd310_table_silver_ordersclean_automaticallypopulated.png)

### 3.4. Create gold layer
3.4.1. It's time to create schema gold and two new tables, which will further filter the data from ```silver.orders_clean``` and ultimately prepare it for final activities like machine learning or business intelligence. I create two tables: 

- `` gold.orders_revenue_daily`` which shows daily revenue I record from orders received at the same day

- ``gold.customer_ltv`` which shows lifetime value of orders put by every client cumulatively

I use similar SQL statement, which creates the ```gold``` schema and both tables by ```CTAS```.

```sql
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE gold.orders_revenue_daily
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['order_date']
)
AS
SELECT
    CAST(created_at AS DATE) AS order_date,
    currency,
    SUM(amount)              AS total_revenue,
    COUNT(*)                 AS order_count
FROM silver.orders_clean
GROUP BY
    CAST(created_at AS DATE),
    currency;

CREATE TABLE gold.customer_ltv
WITH (format = 'PARQUET')
AS
SELECT
    customer_id,
    currency,
    SUM(amount) AS lifetime_value,
    COUNT(*)    AS orders_count
FROM silver.orders_clean
GROUP BY customer_id, currency;
```

3.4.2. The table ```gold.orders_revenue_daily``` was created and populated:

![](img/wxd311_watsonxdata_table_ordersrevenuedaily_createdandpopulated.png)

and so was ```gold.customer_ltv```:
![](img/wxd312_watsonxdata_table_customerltv_createdandpopulated.png)

3.4.3. The final structure created is:

```
iceberg_data
├── bronze
│   └── orders_raw
├── silver
│   └── orders_clean
└── gold
    ├── orders_revenue_daily
    └── customer_ltv
```

### 3.5. Incremental / CDC-ready pattern - bronze
Instead of full reloads of the same source data in PostgreSQL database into Iceberg on and on, I do the incremental add. This also shows why I need the extra columns such as created_at. This approach supports RAG and AI later on, as it ensures auditing and lineage in the table in schema bronze.

3.5.1. Let's start from additional PostgreSQL INSERT statements to add extra orders to the source table:

```sql
INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (11, 109, 1006, 79.90,  'EUR', 'paid',     '2024-11-07 09:10:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (12, 110, 1002, 129.00, 'USD', 'pending',  '2024-11-07 11:45:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (13, 101, 1007, 15.00,  'EUR', 'paid',     '2024-11-08 08:05:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (14, 111, 1003, 19.50,  'USD', 'cancelled','2024-11-08 13:30:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (15, 112, 1008, 499.99, 'USD', 'paid',     '2024-11-09 17:20:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (16, 109, 1001, 49.99,  'EUR', 'shipped',  '2024-11-10 10:00:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (17, 113, 1004, 299.99, 'EUR', 'paid',     '2024-11-10 15:55:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (18, 114, 1005, 9.99,   'USD', 'pending',  '2024-11-11 09:40:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (19, 101, 1002, 129.00, 'USD', 'paid',     '2024-11-11 18:10:00+00');

INSERT INTO orders (id, customer_id, product_id, amount, currency, status, created_at)
VALUES (20, 115, 1009, 59.00,  'EUR', 'paid',     '2024-11-12 07:25:00+00');
```

3.5.2. I check if Presto captures both sources PostgreSQL table ```orders``` new rows and the Iceberg table ```orders_raw``` based on their max created_at value:

```sql
SELECT *
FROM postgres.public.orders
WHERE created_at > (
    SELECT max(created_at) FROM bronze.orders_raw
);
```

It returns just new rows:
![](img/wxd313_watsonxdata_federatedquery_tosee_justnewrows_inpostgres.png)

3.5.3. I merge into ```bronze.orders_raw``` only the new rows:

```sql
INSERT INTO bronze.orders_raw (
    order_id,
    customer_id,
    amount,
    created_at,
    currency
)
SELECT
    order_id,
    customer_id,
    amount,
    created_at,
    CAST(currency AS VARCHAR)
FROM postgres.public.orders
WHERE created_at > (
    SELECT max(created_at) FROM bronze.orders_raw
);
```

It worked out: 
![](img/wxd314_watsonxdata_newrows_added_toordersraw.png)

### 3.5. Incremental / CDC-ready pattern - silver - TBC

### 3.6. Incremental / CDC-ready pattern - gold - TBC





