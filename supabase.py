import datetime
import json
import logging
import os
import random

import pandas as pd
import sqlalchemy
import sqlalchemy.orm
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

import supabase_models as models
from models import Model


def add_weekdays(session: sqlalchemy.orm.Session):
    weekdays = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
    for id, name in weekdays.items():
        try:
            session.add(models.Weekday(id=id, name=name))
            session.commit()
            logging.info(f"Added weekday to Weekday table: {id} {name}")
        except IntegrityError:
            logging.info(f"Weekday(id:{id}, name:{name}) already exists. Skipping.")
            session.rollback()
        except Exception as e:
            logging.error(f"Error adding weekday {id} {name}: {e}")
            session.rollback()


def add_timeslots(session: sqlalchemy.orm.Session):
    start_time = pd.Timestamp("07:00:00")
    end_time = pd.Timestamp("18:00:00")
    minute_index = pd.date_range(start_time, end_time, freq="1min").time

    for id, minute in enumerate(minute_index):
        try:
            session.add(models.TimeSlot(id=id, time=minute))
            session.commit()
            logging.info(f"Added timeslot to Timeslot table: {minute}")
        except IntegrityError:
            logging.info(f"Timeslot(id:{minute}) already exists. Skipping.")
            session.rollback()
        except Exception as e:
            logging.error(f"Error adding timeslot {minute}: {e}")
            session.rollback()


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv(".env")
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not set")
    pass

    engine = sqlalchemy.create_engine(DATABASE_URL)
    SessionLocal = sqlalchemy.orm.sessionmaker(bind=engine)
    Base = sqlalchemy.orm.declarative_base()

    session = SessionLocal()

    with open("./data.json", "r") as f:
        data = json.load(f)

    courses = []

    for course in data["classes"]:
        course = Model(**course)
        courses.append(course)

        db_majors: list[models.Major] = session.query(models.Major).all()
        db_major_names = [major.name for major in db_majors]
        if course.subject not in db_major_names:
            try:
                new_major = models.Major(
                    id=random.randint(1, 2**16 - 1), name=course.subject
                )
                session.add(new_major)
                session.commit()
                logging.info(f"Added Major(id:{new_major.id}, name:{course.subject})")
            except IntegrityError:
                logging.info(f"Major(name:{course.subject}) already exists. Skipping.")
                session.rollback()

    session.commit()
    session.close()


if __name__ == "__main__":
    main()
