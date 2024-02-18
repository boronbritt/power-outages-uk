from providers.sp_energy_networks import update_sp_energy_networks
from providers.nationalgrid import update_national_grid
from providers.uk_power_networks import update_uk_power_networks
from providers.northernpowergrid import update_northern_powergrid
from providers.electricity_north_west import update_electricity_north_west
from providers.ss_electricity_networks import update_ss_electricity_networks
from sqlalchemy.orm import Session
from outage import PowerOutage, create_tables
import sqlalchemy as db
import os
import sys

conn_str = os.environ.get("OUTAGE_CONN_STRING")
engine = db.create_engine(conn_str)

if len(sys.argv) > 1 and sys.argv[1] == "create":
    create_tables(engine)
else:
    update_sp_energy_networks(engine)
    update_national_grid(engine)
    update_uk_power_networks(engine)
    update_northern_powergrid(engine)
    update_electricity_north_west(engine)
    update_ss_electricity_networks(engine)

    with Session(engine) as session:
        session.query(PowerOutage).filter(PowerOutage.active == 1).update({'active': 0})
        session.flush()
        session.query(PowerOutage).filter(PowerOutage.active == 2).update({'active': 1})
        session.commit()