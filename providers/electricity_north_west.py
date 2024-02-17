from outage import PowerOutage, parse_nullable_time, handle_outage
from sqlalchemy.orm import Session
import requests

url = "https://www.enwl.co.uk/power-outages/search?pageSize=99999&postcodeOrReferenceNumber=&pageNumber=1&includeCurrent=true&includeResolved=false&includeTodaysPlanned=false&includeFuturePlanned=false&includeCancelledPlanned=false"


def get_postcodes(row):
    if row["AffectedPostcodes"] == None:
        return []
    return row["AffectedPostcodes"].strip().split(", ")


def update_electricity_north_west(engine):
    # Data is stored in a javascript object so cut out the section where its stored and parse it
    outages = requests.get(url).json()["Items"]

    postcodes = []

    with Session(engine) as session:
        session.begin()
        for row in outages:
            outage = PowerOutage(
                supplier="electricity_north_west",
                customers_affected=row["consumersOff"],
                reference=row["faultNumber"],
                type=row["WebTMSFaultType"],
                start_time=parse_nullable_time(row["date"]),
                end_time=parse_nullable_time(row["estimatedTimeOfRestoration"]),
            )

            postcodes.extend(
                handle_outage(row["faultStatus"], get_postcodes(row), outage, session)
            )

        # Add to database
        session.add_all(postcodes)
        session.commit()
