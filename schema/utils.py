import json
import os

import pandas as pd
import sqlalchemy
import sqlalchemy.orm
from dotenv import load_dotenv
from pandas import json_normalize


def get_df():
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

    df.rename(
        inplace=True,
        columns={
            "crse_id": "courseId",
            "class_section": "sectionCode",
            "strm": "termId",
        },
    )

    df.reset_index(inplace=True, drop=True)
    return df


def get_session():
    load_dotenv(".env")
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL is None:
        raise ValueError("DATABASE_URL is not set")

    engine = sqlalchemy.create_engine(DATABASE_URL)
    SessionLocal = sqlalchemy.orm.sessionmaker(bind=engine)
    session = SessionLocal()
    return session
