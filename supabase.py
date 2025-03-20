import datetime
import json
import os

import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
from pandas import json_normalize

import supabase_models as models

with open("./data2.json") as f:
    json_data = json.load(f)["classes"]

df = pd.DataFrame(json_data)
df = df[
    [
        "crse_id",
        "class_section",
        "enrollment_total",
        "instruction_mode",
        "strm",
        "subject",
        "subject_descr",
        "meetings",
    ]
]

df = df.explode("meetings")
meetings = json_normalize(df["meetings"])
meetings = meetings[["days", "start_time", "end_time"]]
df = df.drop(columns=["meetings"]).reset_index(drop=True)
df = pd.concat([df, meetings], axis=1)

df = df[df.days != "TBA"]

df.start_time = pd.to_datetime(df.start_time, format="%H.%M.%S.000000").dt.time
df.end_time = pd.to_datetime(df.end_time, format="%H.%M.%S.000000").dt.time

df["mo"] = df.days.str.contains("Mo")
df["tu"] = df.days.str.contains("Tu")
df["we"] = df.days.str.contains("We")
df["th"] = df.days.str.contains("Th")
df["fr"] = df.days.str.contains("Fr")

# df.drop(columns=["days"], inplace=True)

min_time = pd.Timestamp(df.start_time.min().strftime("%H:%M:%S"))
max_time = pd.Timestamp(df.end_time.max().strftime("%H:%M:%S"))
time_range = pd.date_range(min_time, max_time, freq="1min").time
timeSlotTable = pd.DataFrame(time_range).rename(columns={0: "time"}).reset_index(drop=True)

termTable = pd.DataFrame(df.strm.unique()).reset_index(drop=True)
weekdayTable = pd.DataFrame(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
).rename(columns={0: "weekday"})

weekday_mapping = {"Mo": 1, "Tu": 2, "We": 3, "Th": 4, "Fr": 5}

courseTable = (
    df[["crse_id", "subject"]]
    .drop_duplicates()
    .rename(columns={"crse_id": "courseId", "subject": "major"})
)
sessionTable = (
    df[["crse_id", "strm", "class_section", "instruction_mode"]]
    .reset_index(drop=True)
    .rename(
        columns={
            "crse_id": "courseId",
            "strm": "termId",
            "class_section": "section",
            "instruction_mode": "instructionMode",
        }
    )
)

occupancyTable = pd.DataFrame()
for index, row in df.iterrows():
    start_time = pd.Timestamp(row.start_time.strftime("%H:%M:%S"))
    end_time = pd.Timestamp(row.end_time.strftime("%H:%M:%S"))
    time_index = pd.date_range(start_time, end_time, freq="1min").time

    for weekday in ["Mo", "Tu", "We", "Th", "Fr"]:
        if weekday not in row["days"]:
            continue
        occSubTable = pd.DataFrame()
        occSubTable["time"] = time_index
        occSubTable["sessionId"] = row["strm"]
        occSubTable["courseId"] = row["crse_id"]
        occSubTable["weekdayId"] = weekday_mapping[weekday]
        occSubTable["studentCount"] = row["enrollment_total"]
        occSubTable["timeSlotId"] = timeSlotTable[
            timeSlotTable["time"].isin(time_index)
        ].index
        occupancyTable = pd.concat([occupancyTable, occSubTable])

occupancyTable.reset_index(drop=True, inplace=True)

load_dotenv(".env")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set")
pass

engine = sqlalchemy.create_engine(DATABASE_URL)
SessionLocal = sqlalchemy.orm.sessionmaker(bind=engine)
Base = sqlalchemy.orm.declarative_base()

session = SessionLocal()

time_slots = [
    models.TimeSlot(id=i, time=t) for i, t in enumerate(timeSlotTable["time"])
]
terms = [models.Term(id=i, name=t) for i, t in enumerate(termTable[0])]
weekdays = [
    models.Weekday(id=v, name=k)
    for k, v in {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
    }.items()
]

courses = [
    models.Course(id=row.courseId, major=row.major) for _, row in courseTable.iterrows()
]
occupancy = [
    models.Occupancy(
        id=index,
        sessionId=row.sessionId,
        weekdayId=row.weekdayId,
        timeSlotId=row.timeSlotId,
        studentCount=row.studentCount,
    )
    for index, row in occupancyTable.iterrows()
]

sessions = [
    models.Session(
        id=index,
        courseId=row.courseId,
        termId=row.termId,
        classSection=row.section,
        instructionMode=row.instructionMode,
    )
    for index, row in sessionTable.iterrows()
]

session.add_all(time_slots)
session.add_all(terms)
session.add_all(weekdays)
session.add_all(courses)
session.commit()
session.add_all(sessions)
session.add_all(occupancy)
session.commit()
session.close()

print(courses)
