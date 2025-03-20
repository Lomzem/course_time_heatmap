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
    db_weekdays = [row[0] for row in session.query(models.Weekday.name).all()]

    for id, name in weekdays.items():
        if name in db_weekdays:
            logging.info(f"Weekday(id:{id}, name:{name}) already exists. Skipping.")
            continue
        try:
            session.add(models.Weekday(id=id, name=name))
            session.commit()
            logging.info(f"Added weekday to Weekday table: {id} {name}")
            db_weekdays.append(name)
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

    db_timeslots = [row[0] for row in session.query(models.TimeSlot.time).all()]

    for id, minute in enumerate(minute_index):
        if minute in db_timeslots:
            logging.info(f"Timeslot(id:{minute}) already exists. Skipping.")
            continue
        try:
            session.add(models.TimeSlot(id=id, time=minute))
            session.commit()
            logging.info(f"Added timeslot to Timeslot table: {minute}")
            db_timeslots.append(minute)
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

    add_weekdays(session)
    add_timeslots(session)

    with open("./data.json", "r") as f:
        data = json.load(f)

    courses = []
    db_course_ids = [row[0] for row in session.query(models.Course.id).all()]
    db_majors = session.query(models.Major).all()
    db_major_names = [major.name for major in db_majors]
    major_map = {major.name: major.id for major in db_majors}

    for course in data["classes"]:
        course = Model(**course)
        courses.append(course)

        if course.subject not in db_major_names:
            try:
                new_major = models.Major(
                    id=random.randint(1, 2**16 - 1), name=course.subject
                )
                session.add(new_major)
                session.commit()
                logging.info(f"Added Major(id:{new_major.id}, name:{course.subject})")
                db_major_names.append(course.subject)
                major_map[course.subject] = new_major.id
            except IntegrityError:
                logging.info(f"Major(name:{course.subject}) already exists. Skipping.")
                session.rollback()

        if course.crse_id not in db_course_ids:
            try:
                new_course = models.Course(id=course.crse_id, majorId=major_map[course.subject])
                session.add(new_course)
                session.commit()
                logging.info(f"Added Course(id:{new_course.id}, majorId:{major_map[course.subject]})")
                db_course_ids.append(course.crse_id)
            except IntegrityError:
                logging.info(f"Course(id:{course.crse_id}) already exists. Skipping.")
                session.rollback()

    session.commit()
    session.close()


if __name__ == "__main__":
    main()
