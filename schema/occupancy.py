import pandas as pd
import sqlalchemy
from session import get_session_mapping
from supabase_models import Occupancy
from utils import get_df, get_session
from weekday import get_weekday_mapping


def get_occupancy_mapping():
    db_session = get_session()
    occupancies = db_session.query(Occupancy).all()
    db_session.close()
    # print(occupancies)
    return {f"{o.sessionId}{o.time}{o.weekdayId}": o.id for o in occupancies}


def add_occupancy():
    db_session = get_session()
    df = get_df()
    df = df[["courseId", "termId", "sectionCode", "days", "enrollment_total", "start_time", "end_time"]]
    df.courseId = df.courseId.astype(int)
    df.sectionCode = df.sectionCode.astype(int)

    df = df.drop_duplicates()

    df.days = df.days.apply(lambda x: [x[i : i + 2] for i in range(0, len(x), 2)])
    df = df.explode("days", ignore_index=True)

    df["sessionCompositeKey"] = (
        df.courseId.astype(str) + df.termId.astype(str) + df.sectionCode.astype(str)
    )
    df["sessionId"] = df.sessionCompositeKey.map(get_session_mapping())

    start_time = pd.Timestamp("07:00:00")
    end_time = pd.Timestamp("18:00:00")
    minute_index = pd.date_range(start_time, end_time, freq="5min").time
    df["time"] = [minute_index] * len(df)

    df = df.explode("time", ignore_index=True)

    weekday_map = get_weekday_mapping()
    weekday_map = {k[:2]: v for k, v in weekday_map.items()}
    df["weekdayId"] = df.days.map(weekday_map)

    df["compositeKey"] = (
        df.sessionId.astype(str) + df.time.astype(str) + df.weekdayId.astype(str)
    )

    df = df.drop_duplicates()
    df = df[~df.compositeKey.isin(get_occupancy_mapping().keys())]

    occupancies = [
        Occupancy(
            sessionId=row.sessionId,
            time=row.time,
            weekdayId=row.weekdayId,
            enrollmentTotal=row.enrollment_total,
        )
        for _, row in df.iterrows()
    ]

    db_session.add_all(occupancies)
    db_session.commit()
    db_session.close()

if __name__ == "__main__":
    add_occupancy()
