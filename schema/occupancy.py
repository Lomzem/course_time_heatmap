import pandas as pd
import sqlalchemy
from course import get_course_mapping
from major import get_major_mapping
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


def group_explode_times(group):
    # Assume all rows in group have the same start and end times
    sample = group.iloc[0]
    start = pd.Timestamp(str(sample["start_time"]))
    end = pd.Timestamp(str(sample["end_time"]))
    times = pd.date_range(start, end, freq="5min").time
    group["time"] = [times] * len(group)
    group = group.explode("time", ignore_index=True)
    return group


def add_occupancy():
    db_session = get_session()
    df = get_df()
    df = df[
        [
            "catalog_nbr",
            "days",
            "end_time",
            "enrollment_total",
            "sectionCode",
            "start_time",
            "subject",
            "termId",
            "instruction_mode",
        ]
    ]
    df.sectionCode = df.sectionCode.astype(int)

    df = df[df.instruction_mode == "P"]
    df = df[df.enrollment_total > 0]

    df = df.drop_duplicates()

    df.days = df.days.apply(lambda x: [x[i : i + 2] for i in range(0, len(x), 2)])
    df = df.explode("days", ignore_index=True)

    df["subjectId"] = df.subject.map(get_major_mapping())
    df["courseIdCompositeKey"] = (
        df.subjectId.astype(str) + "" + df.catalog_nbr.astype(str)
    )
    df["courseId"] = df.courseIdCompositeKey.map(get_course_mapping())

    df["sessionCompositeKey"] = (
        df.courseId.astype(str) + df.termId.astype(str) + df.sectionCode.astype(str)
    )
    df["sessionId"] = df.sessionCompositeKey.map(get_session_mapping())

    df = df.groupby("sessionId", group_keys=False).apply(group_explode_times)

    weekday_map = get_weekday_mapping()
    weekday_map = {k[:2]: v for k, v in weekday_map.items()}
    df["weekdayId"] = df.days.map(weekday_map)
    print(df.days.unique())
    print(df.weekdayId.unique())

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

    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", None)
    # print(df[["sessionId", "time", "weekdayId", "enrollment_total"]])

    db_session.add_all(occupancies)
    db_session.commit()
    db_session.close()


if __name__ == "__main__":
    add_occupancy()
