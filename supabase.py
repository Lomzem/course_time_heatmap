import logging
import os

import sqlalchemy
import sqlalchemy.orm
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

import supabase_models as models


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


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv(".env")
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not set")
    pass

    engine = sqlalchemy.create_engine(DATABASE_URL)
    SessionLocal = sqlalchemy.orm.sessionmaker(bind=engine)
    # Base = sqlalchemy.orm.declarative_base()

    session = SessionLocal()
    add_weekdays(session)

    weekdays = session.query(models.Weekday).all()
    for weekday in weekdays:
        print(f"{weekday.id} {weekday.name}")

    session.commit()
    session.close()


if __name__ == "__main__":
    main()
