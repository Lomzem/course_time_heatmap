import json
import os

import pandas as pd
import sqlalchemy
import sqlalchemy.orm
from dotenv import load_dotenv
from pandas import json_normalize


def get_df():
    with open("./data.json") as f:
        json_data = json.load(f)

    df = pd.DataFrame(json_data)
    df = df[
        [
            "catalog_nbr",
            "class_section",
            "enrollment_total",
            "instruction_mode",
            "meetings",
            "strm",
            "subject",
            "subject_descr",
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
