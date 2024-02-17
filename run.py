from providers.spenergy import update_sp_energy_networks
from providers.nationalgrid import update_national_grid
from providers.uk_power_networks import update_uk_power_networks
from providers.northernpowergrid import update_northern_powergrid
from providers.electricity_north_west import update_electricity_north_west
import sqlalchemy as db
import os

conn_str = os.environ.get("OUTAGE_CONN_STRING")

engine = db.create_engine(conn_str)
update_sp_energy_networks(engine)
update_national_grid(engine)
update_uk_power_networks(engine)
update_northern_powergrid(engine)
update_electricity_north_west(engine)
