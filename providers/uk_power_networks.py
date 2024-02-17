from outage import PowerOutage, parse_nullable_time, handle_outage
from sqlalchemy.orm import Session
import requests


def get_status(row):
    matches = [x for x in row["Steps"] if x["Active"] == True]
    if len(matches) > 0:
        return matches[0]["Message"]
    return None


def update_uk_power_networks(engine):
    # Data is stored in a javascript object so cut out the section where its stored and parse it
    outages = requests.get(
        "https://www.ukpowernetworks.co.uk/api/power-cut/all-incidents-light"
    ).json()

    postcodes = []

    with Session(engine) as session:
        session.begin()
        for row in outages:
            outage = PowerOutage(
                supplier="uk_power_networks",
                customers_affected=row["NoCustomerAffected"],
                reference=row["IncidentReference"],
                type=row["PowerCutType"],
                start_time=parse_nullable_time(row["CreationDateTime"]),
                end_time=parse_nullable_time(row["EstimatedRestorationDate"]),
            )

            postcodes.extend(
                handle_outage(get_status(row), row["FullPostcodeData"], outage, session)
            )

        # Add to database
        session.add_all(postcodes)
        session.commit()
