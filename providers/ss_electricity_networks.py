from outage import PowerOutage, parse_nullable_time, handle_outage
from sqlalchemy.orm import Session
import requests


def get_customer_count(row):
    if "affectedCustomerCount" not in row.keys():
        return None
    return row["affectedCustomerCount"]


def get_start_time(row):
    if "loggedAt" not in row.keys():
        return None
    return parse_nullable_time(row["loggedAt"])


def get_estimated_restoration(row):
    if "estimatedRestoration" not in row.keys():
        return None
    return parse_nullable_time(row["estimatedRestoration"])


def update_ss_electricity_networks(engine):
    # Data is stored in a javascript object so cut out the section where its stored and parse it
    outages = requests.get(
        "https://ssen-powertrack-api.opcld.com/gridiview/reporter/info/livefaults"
    ).json()["Faults"]

    postcodes = []

    with Session(engine) as session:
        session.begin()
        for row in outages:
            outage = PowerOutage(
                supplier="ss_electricity_networks",
                customers_affected=get_customer_count(row),
                active=2,
                reference=row["reference"],
                type=row["type"],
                start_time=get_start_time(row),
                end_time=get_estimated_restoration(row),
            )

            postcodes.extend(
                handle_outage(row["message"], row["affectedAreas"], outage, session)
            )

        # Add to database
        session.add_all(postcodes)
        session.commit()
