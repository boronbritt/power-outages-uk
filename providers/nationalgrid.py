from io import StringIO
from outage import PowerOutage, parse_nullable_time, handle_outage
from sqlalchemy.orm import Session
import csv
import requests


def parse_csv(data):
    f = StringIO(data)
    reader = csv.reader(f, delimiter=",")
    next(reader, None)  # Skip CSV Header
    return reader


def update_national_grid(engine):
    # Get URL to the latest outage resource
    resources = requests.get(
        "https://connecteddata.nationalgrid.co.uk/dataset/live-power-cuts/datapackage.json"
    ).json()
    url = resources["resources"][0]["url"]

    # Get current outage data
    csv_data = requests.get(url).text

    postcodes = []

    with Session(engine) as session:
        session.begin()
        for row in parse_csv(csv_data):
            outage = PowerOutage(
                supplier="national_grid",
                customers_affected=row[3],
                reference=row[2],
                type=row[8],
                start_time=parse_nullable_time(row[10]),
                end_time=parse_nullable_time(row[10]),
            )

            postcodes.extend(handle_outage(row[6], row[15].split(","), outage, session))

        # Add to database
        session.add_all(postcodes)
        session.commit()
