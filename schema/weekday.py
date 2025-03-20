import sqlalchemy
from supabase_models import Weekday
from utils import get_session

WEEKDAY_MAPPING = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
}


def get_weekday_mapping():
    return WEEKDAY_MAPPING


def add_weekday():
    session = get_session()
    weekdays = [
        Weekday(id=value, name=key, abbr=key[0:2])
        for key, value in WEEKDAY_MAPPING.items()
    ]
    for weekday in weekdays:
        try:
            session.add(weekday)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            print(f"Duplicate: Skipping Weekday({weekday.name})")
            continue
        else:
            print(f"Added weekday {weekday.name}")

    session.close()


if __name__ == "__main__":
    add_weekday()
