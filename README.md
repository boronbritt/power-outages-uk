UK Power Outage Scraper

This tool scrapes power outage data from 6 of the united kingdoms most popular power providers, this data is then stored in 3 SQL tables: 
"PowerOutages", "PowerOutagePostcodes" and "PowerOutageStatus". The SQL connection is made by SQlAlchemy using a connection string stored in 
the environment variable "OUTAGE_CONN_STRING", you may need to install some librarys required by sql alchemy for your database.
