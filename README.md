## UK Power Outage Scraper

This tool scrapes power outage data from 6 of the united kingdoms most popular power providers, this data is then stored in 3 SQL tables: 
"PowerOutages", "PowerOutagePostcodes" and "PowerOutageStatus". The SQL connection is made by SQlAlchemy using a connection string stored in 
the environment variable "OUTAGE_CONN_STRING", you may need to install some librarys required by sql alchemy for your database.

To create the SQL tables you can either run the run.py script as such
```bash
python3 run.py create
```

Or create them manually from these SQL statements
```sql
CREATE TABLE public."PowerOutagePostcodes" (
	id serial4 NOT NULL,
	postcode varchar(9) NOT NULL,
	outage_id int4 NOT NULL,
	CONSTRAINT "PowerOutagePostcodes_pkey" PRIMARY KEY (id)
);

CREATE TABLE public."PowerOutageStatus" (
	id serial4 NOT NULL,
	status varchar NOT NULL,
	"time" timestamp NULL,
	outage_id int4 NOT NULL,
	CONSTRAINT "PowerOutageStatus_pkey" PRIMARY KEY (id),
	CONSTRAINT "_status_constraint" UNIQUE (outage_id, status)
);

CREATE TABLE public."PowerOutages" (
	id serial4 NOT NULL,
	customers_affected int4 NULL,
	start_time timestamp NULL,
	end_time timestamp NULL,
	reference varchar(42) NOT NULL,
	"type" varchar(32) NOT NULL,
	supplier public."power_supplier" NOT NULL,
	CONSTRAINT "PowerOutages_pkey" PRIMARY KEY (id),
	CONSTRAINT "_reference_constraint" UNIQUE (supplier, reference)
);
```

### Usage
Once this has been setup correctly you can run the script with 
```bash
export OUTAGE_CONN_STRING="CONNECTION_STRING_HERE"
python3 run.py
```
from this it should be trivial to gather power outage over time using a cronjob or something similar
