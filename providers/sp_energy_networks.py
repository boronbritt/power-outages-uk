from outage import PowerOutage, parse_nullable_time, handle_outage
from sqlalchemy.orm import Session
import requests
import json
import re


# Required headers due to Akamai WAF blocking plain requests
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "br",
}


def update_sp_energy_networks(engine):
    # Data is stored in a javascript object so cut out the section where its stored and parse it
    data = requests.get(
        "https://www.spenergynetworks.co.uk/pages/power_cuts_map.aspx", headers=headers
    ).text
    json_string = re.search(
        "arrPowercutsPostcodes:(.*),strPagePathListView", data
    ).group(1)
    outages = json.loads(json_string)

    postcodes = []

    with Session(engine) as session:
        session.begin()
        for row in outages:
            outage = PowerOutage(
                supplier="sp_energy_networks",
                reference=row["INCIDENT_REF"],
                type=row["INC_TYPE_ID"],
                start_time=parse_nullable_time(row["CREATION_DATE"]),
                end_time=parse_nullable_time(row["EST_REST_DATE"]),
            )

            postcodes.extend(
                handle_outage(
                    row["LOOK_UP_DESCRIPTION"], row["POSTCODES"], outage, session
                )
            )

        # Add to database
        session.add_all(postcodes)
        session.commit()
