from sqlalchemy import TIMESTAMP, Column, Integer, String, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MacroEvents(Base):
    __tablename__ = "macro_events"
    __table_args__ = {"schema": "core"}
    hash = Column(String, nullable=False, primary_key=True)
    event = Column(String)
    importance = Column(String)
    timestamp = Column(TIMESTAMP(timezone=False))  # Adjusted for no timezone
    flag = Column(String)
    previous = Column(Integer)
    forecast = Column(Integer)
    actual = Column(Integer)
    process_time = Column(
        TIMESTAMP(timezone=True), server_default=text("'CURRENT_TIMESTAMP'")
    )

    def __init__(self, json_data):
        self.hash = json_data.get("hash")
        self.event = json_data.get("event")
        self.importance = json_data.get("importance")
        self.timestamp = json_data.get("timestamp")
        self.flag = json_data.get("flag")
        self.previous = json_data.get("previous")
        self.forecast = json_data.get("forecast")
        self.actual = json_data.get("actual")
        self.process_time = json_data.get("process_time")


class MacroEventsStore:
    @staticmethod
    def write_all(
        session, json_data_list: list, merge: bool = False, commit: bool = True
    ):
        with session:
            stmt = pg_insert(MacroEvents).values(json_data_list)
            if json_data_list:
                if merge:
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["hash"],
                        set_={
                            "event": stmt.excluded.event,
                            "importance": stmt.excluded.importance,
                            "timestamp": stmt.excluded.timestamp,
                            "flag": stmt.excluded.flag,
                            "previous": stmt.excluded.previous,
                            "forecast": stmt.excluded.forecast,
                            "actual": stmt.excluded.actual,
                            "process_time": stmt.excluded.process_time,
                        },
                    )
                    session.execute(stmt)
                if commit:
                    session.commit()
