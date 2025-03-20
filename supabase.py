import json
import logging
import os

import pandas as pd
import sqlalchemy
import sqlalchemy.orm
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

import supabase_models as models
from models import Model


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

    start_time = pd.Timestamp("07:00:00")
    end_time = pd.Timestamp("18:00:00")
    minute_index = pd.date_range(start_time, end_time, freq="1min").time

    # db_timeslots = [row[0] for row in session.query(models.TimeSlot.time).all()]
    db_timeslots = session.query(models.TimeSlot).all()
    timeslots_map = {timeslot.time: timeslot.id for timeslot in db_timeslots}
    # occupancy_map = {f}

    for id, minute in enumerate(minute_index):
        if minute in timeslots_map.keys():
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

    with open("./data.json", "r") as f:
        data = json.load(f)

    courses = []

    db_course_ids = [row[0] for row in session.query(models.Course.id).all()]

    db_majors = session.query(models.Major).all()
    db_major_names = [major.name for major in db_majors]
    major_map = {major.name: major.id for major in db_majors}

    db_sessions = session.query(models.Session).all()
    sessions_map = {
        f"{s.courseId}{s.termId}{s.classSection}": s.id for s in db_sessions
    }

    db_occupancies = session.query(models.Occupancy).all()
    occupancy_map = {
        f"{o.sessionId}{o.weekdayId}{o.timeSlotId}": o.id for o in db_occupancies
    }

    for course in data["classes"]:
        course = Model(**course)
        courses.append(course)

        # Insert Major
        if course.subject not in db_major_names:
            try:
                new_major = models.Major(
                    name=course.subject
                )
                session.add(new_major)
                session.commit()
                logging.info(f"Added Major(id:{new_major.id}, name:{course.subject})")
                db_major_names.append(course.subject)
                major_map[course.subject] = new_major.id
            except IntegrityError:
                logging.info(f"Major(name:{course.subject}) already exists. Skipping.")
                session.rollback()

        # Insert Course
        if course.crse_id not in db_course_ids:
            try:
                new_course = models.Course(
                    id=course.crse_id, majorId=major_map[course.subject]
                )
                session.add(new_course)
                session.commit()
                logging.info(
                    f"Added Course(id:{new_course.id}, majorId:{major_map[course.subject]})"
                )
                db_course_ids.append(course.crse_id)
            except IntegrityError:
                logging.info(
                    f"Course(id:{course.crse_id}, termId:{course.strm}, classSection:{course.class_section}) already exists. Skipping."
                )
                session.rollback()

        # Insert Session
        if (
            f"{int(course.crse_id)}{int(course.strm)}{int(course.class_section)}"
            not in sessions_map.keys()
        ):
            instruction_mode = (
                "inperson"
                if course.instruction_mode.lower() == "p"
                else "virtual"
            )

            new_session = models.Session(
                courseId=course.crse_id,
                termId=course.strm,
                classSection=course.class_section,
                instructionMode=instruction_mode,
            )

            try:
                session.add(new_session)
                session.commit()
                logging.info(
                    f"Added Session(id:{new_session.id}, courseId:{course.crse_id}, termId:{course.strm}, classSection:{course.class_section}, instructionMode:{instruction_mode})"
                )
                sessions_map[f"{course.crse_id}{course.strm}{course.class_section}"] = (
                    new_session.id
                )
            except IntegrityError:
                logging.info(f"Session(id:{new_session.id}) already exists. Skipping.")
                session.rollback()
        else:
            logging.info(f"Session(courseId:{course.crse_id}, termId:{course.strm}, classSection:{course.class_section}) already exists. Skipping.")

        # Insert Occupancy
                # f"{o.sessionId}{o.weekdayId}{o.timeSlotId}": o.id for o in db_occupancies

        weekdays = {"Mo": 1, "Tu": 2, "We": 3, "Th": 4, "Fr": 5}
        includes_weekdays = set()
        for day in weekdays.keys():
            if not course.meetings:
                continue
            if day in course.meetings[0].days:
                includes_weekdays.add(day)

        for time in timeslots_map.keys():
            if not course.meetings:
                continue
            if not time:
                continue

            session_id = sessions_map[f"{int(course.crse_id)}{int(course.strm)}{int(course.class_section)}"]
            time_slot_id = timeslots_map[time]

            if start_time.time() <= time <= end_time.time():
                for day in weekdays:
                    weekday_Id = weekdays[day]

                    if (f"{session_id}{weekday_Id}{time_slot_id}") not in occupancy_map.keys():
                        new_occupancy = models.Occupancy(
                            sessionId=session_id,
                            weekdayId=weekday_Id,
                            timeSlotId=time_slot_id,
                            studentCount=course.enrollment_total,
                        )
                        try:
                            session.add(new_occupancy)
                            session.commit()
                            logging.info(
                                f"Added Occupancy(id:{new_occupancy.id}, sessionId:{session_id}, weekdayId:{weekdays[day]}, timeSlotId:{time_slot_id}, studentCount:{course.enrollment_total})"
                            )
                            occupancy_map[
                                f"{int(course.crse_id)}{int(course.strm)}{int(course.class_section)}{weekdays[day]}{timeslots_map[time]}"
                            ] = new_occupancy.id
                        except IntegrityError:
                            logging.info(
                                f"Occupancy(id:{new_occupancy.id}, sessionId:{session_id}, weekdayId:{weekdays[day]}, timeSlotId:{timeslots_map[time]}, studentCount:{course.enrollment_total}) already exists. Skipping."
                            )
                            session.rollback()
                    else:
                        logging.info(
                            f"Occupancy(sessionId:{sessions_map[f'{int(course.crse_id)}{int(course.strm)}{int(course.class_section)}']}) already exists. Skipping."
                        )

    session.commit()
    session.close()


if __name__ == "__main__":
    main()
