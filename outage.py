from typing import List
from typing import Optional
from datetime import datetime
from dateutil import parser
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import sqlalchemy as db


def parse_nullable_time(t):
    if not t:
        return None
    return parser.parse(t)


class Base(DeclarativeBase):
    pass


class PowerOutage(Base):
    __tablename__ = "PowerOutages"
    __table_args__ = (UniqueConstraint(
        "supplier", "reference", name="_reference_constraint"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    customers_affected: Mapped[Optional[int]] = mapped_column()
    start_time: Mapped[Optional[datetime]] = mapped_column(db.DateTime)
    end_time: Mapped[Optional[datetime]] = mapped_column(db.DateTime)
    reference: Mapped[str] = mapped_column(db.String(42))
    type: Mapped[str] = mapped_column(db.String(32))
    supplier: Mapped[List[str]] = mapped_column(db.Enum(
        "uk_power_networks",
        "national_grid",
        "sp_energy_networks",
        "northern_powergrid",
        "ss_electricity_networks",
        "electricity_north_west",
        "northern_ireland_electricity_networks",
        name="power_supplier"
    ))
    postcodes: Mapped[List["PowerOutagePostcode"]] = relationship(
        back_populates="outage", cascade="all, delete-orphan"
    )
    statuses: Mapped[List["PowerOutageStatus"]] = relationship(
        back_populates="outage", cascade="all, delete-orphan"
    )


class PowerOutagePostcode(Base):
    __tablename__ = "PowerOutagePostcodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    postcode: Mapped[str] = mapped_column(db.String(9))
    outage_id: Mapped[int] = mapped_column(db.ForeignKey("PowerOutages.id"))
    outage: Mapped["PowerOutage"] = relationship(back_populates="postcodes")


class PowerOutageStatus(Base):
    __tablename__ = "PowerOutageStatus"
    __table_args__ = (UniqueConstraint(
        "outage_id", "status", name="_status_constraint"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(db.String)
    time: Mapped[Optional[datetime]] = mapped_column(db.DateTime)
    outage_id: Mapped[int] = mapped_column(db.ForeignKey("PowerOutages.id"))
    outage: Mapped["PowerOutage"] = relationship(back_populates="statuses")


# Update an outage with new information
def update_from_outage(outage, session):
    stmt = db.update(PowerOutage).values(
        supplier=outage.supplier,
        customers_affected=outage.customers_affected,
        reference=outage.reference,
        type=outage.type,
        start_time=outage.start_time,
        end_time=outage.end_time
    ).where(PowerOutage.reference == outage.reference and PowerOutage.supplier == outage.supplier)
    session.execute(stmt)


# Add a status only if the outage is new or the status has changed
def add_status(status, outage, session):
    try:
        outage_query = session.query(
            PowerOutage.id,
            db.sql.expression.literal(datetime.now()),
            db.sql.expression.literal(status)
        ).filter_by(reference=outage.reference, supplier=outage.supplier)
        session.execute(db.insert(PowerOutageStatus).from_select(
            (PowerOutageStatus.outage_id, PowerOutageStatus.time, PowerOutageStatus.status), outage_query))
        session.commit()
    except db.exc.IntegrityError:
        session.rollback()


# Add outage/status and return back a list of postcodes to be added in bulk later
def handle_outage(status, postcodes, outage, session):
    return_postcodes = []
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
        for postcode in postcodes:
            return_postcodes.append(PowerOutagePostcode(
                postcode=postcode, outage=outage))
    finally:
        add_status(status, outage, session)
        return return_postcodes

def create_tables(engine):
    Base.metadata.create_all(engine)