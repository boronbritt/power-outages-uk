from outage import (
    PowerOutage,
    PowerOutagePostcode,
    parse_nullable_time,
    update_from_outage,
    add_status,
)
from sqlalchemy.orm import Session
import requests
import sqlalchemy as db


def update_northern_powergrid(engine):
    # Data is stored in a javascript object so cut out the section where its stored and parse it
    outages = requests.get(
        "https://power.northernpowergrid.com/Powercut_API/rest/powercuts/getall"
    ).json()
    added_outages = []

    postcodes = []

    with Session(engine) as session:
        session.begin()
        for row in outages:
            matches = [x for x in added_outages if x.reference == row["Reference"]]
            if len(matches) > 0:
                postcodes.append(
                    PowerOutagePostcode(postcode=row["Postcode"], outage=matches[0])
                )
                continue

            outage = PowerOutage(
                supplier="northern_powergrid",
                customers_affected=row["TotalConfirmedPowercut"],
                reference=row["Reference"],
                type=row["Type"],
                start_time=parse_nullable_time(row["InsertDate"]),
                end_time=parse_nullable_time(row["EstimatedTimeTillResolution"]),
            )

            try:
                session.add(outage)
                session.commit()
            except db.exc.IntegrityError:
                # If reference already exists just update
                session.rollback()
                update_from_outage(outage, session)
                session.commit()
            else:
                # If adding then also add postcodes
                postcodes.append(
                    PowerOutagePostcode(postcode=row["Postcode"], outage=outage)
                )
                added_outages.append(outage)
            finally:
                add_status(row["CustomerStageSequenceMessage"], outage, session)

        # Add to database
        session.add_all(postcodes)
        session.commit()
